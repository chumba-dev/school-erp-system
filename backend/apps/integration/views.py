import uuid
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import APIKey, LostBookEvent
from .serializers import APIKeySerializer, LostBookEventSerializer
from apps.accounts.permissions import IsAdmin, IsBursar

from apps.common.mixins import SchoolFilterMixin

from apps.finance.models import InvoiceLineItem, FeeInvoice
from apps.core.models import Student, Staff
from apps.academics.models import AcademicYear, Term
from apps.audit.utils import log_custom_action

# ---------- API Key Management (Admin only) ----------
class APIKeyViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [IsAdmin]

    def perform_create(self, serializer):
        # Generate a unique API key
        key = uuid.uuid4().hex
        serializer.save(created_by=self.request.user.staff_profile, key=key)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        api_key = self.get_object()
        old_status = api_key.is_active
        api_key.is_active = False
        api_key.save()
        log_custom_action(
            action='REVOKE',
            table_name='integration_apikey',
            record_id=api_key.id,
            old_values={'is_active': old_status},
            new_values={'is_active': False}
        )
        return Response({'status': 'revoked'})

# ---------- LMS Endpoints (authenticated via API key) ----------
@api_view(['POST'])
@permission_classes([])  # no DRF auth; we'll check API key header manually
def lost_book_event(request):
    """
    LMS calls this endpoint to report a lost book.
    Expects an `X-API-Key` header with a valid API key.
    Payload: {
        "student_admission_number": "STU001",
        "book_number": "KS712/26",
        "book_title": "Biology Textbook",
        "subject": "Biology",
        "academic_year_id": "uuid",
        "term_id": "uuid",
        "loss_date": "2026-06-14"
    }
    """
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return Response({'error': 'API key required'}, status=401)
    try:
        key_obj = APIKey.objects.get(key=api_key, is_active=True)
        if key_obj.expires_at and key_obj.expires_at < timezone.now():
            return Response({'error': 'API key expired'}, status=401)
        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=['last_used_at'])
    except APIKey.DoesNotExist:
        return Response({'error': 'Invalid API key'}, status=401)

    # Validate payload
    data = request.data
    admission_number = data.get('student_admission_number')
    if not admission_number:
        return Response({'error': 'student_admission_number required'}, status=400)
    try:
        student = Student.objects.get(admission_number=admission_number)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)

    # Create lost book event
    event = LostBookEvent.objects.create(
        student=student,
        book_number=data.get('book_number'),
        book_title=data.get('book_title'),
        subject=data.get('subject'),
        academic_year_id=data.get('academic_year_id'),
        term_id=data.get('term_id'),
        loss_date=data.get('loss_date'),
        fee_amount=data.get('fee_amount'),
        lms_sync_status='pending'
    )
    # Optionally create an invoice line item automatically? We'll leave that to bursar.
    return Response({'status': 'received', 'event_id': str(event.id)})

@api_view(['GET'])
@permission_classes([])
def student_clearance_status(request, admission_number):
    """
    LMS checks if a student has any outstanding lost book fees.
    Returns cleared=True if no unpaid lost book fees.
    """
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return Response({'error': 'API key required'}, status=401)
    try:
        key_obj = APIKey.objects.get(key=api_key, is_active=True)
        if key_obj.expires_at and key_obj.expires_at < timezone.now():
            return Response({'error': 'API key expired'}, status=401)
        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=['last_used_at'])
    except APIKey.DoesNotExist:
        return Response({'error': 'Invalid API key'}, status=401)

    try:
        student = Student.objects.get(admission_number=admission_number)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)

    # Check if there are any lost book events that are not cleared
    unresolved = LostBookEvent.objects.filter(student=student, is_cleared=False).exists()
    return Response({
        'cleared': not unresolved,
        'admission_number': admission_number,
        'student_name': f"{student.first_name} {student.last_name}"
    })

@api_view(['POST'])
@permission_classes([])
def webhook_receiver(request, webhook_name):
    """
    Generic webhook endpoint for external systems.
    You can implement specific logic based on webhook_name.
    For LMS, we can have a dedicated endpoint; this is optional.
    """
    api_key = request.headers.get('X-API-Key')
    # Validate API key (same as above)
    # Then process according to webhook_name
    return Response({'status': 'received', 'webhook': webhook_name})


@api_view(['GET'])
@permission_classes([])   # manual API key check
def sync_students(request):
    """
    LMS calls this to get list of all students.
    Supports optional `updated_since` parameter (ISO datetime) for delta sync.
    """
    api_key = _validate_api_key(request)  # we'll define a helper
    if api_key is None:
        return Response({'error': 'Invalid or missing API key'}, status=401)

    updated_since = request.query_params.get('updated_since')
    qs = Student.objects.all().select_related('class_obj', 'stream')
    if updated_since:
        qs = qs.filter(updated_at__gte=updated_since)
    data = []
    for s in qs:
        data.append({
            'admission_number': s.admission_number,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'class': s.class_obj.name if s.class_obj else None,
            'stream': s.stream.name if s.stream else None,
            'parent_phone': s.parent_phone,
            'parent_email': s.parent_email,
            'status': s.enrollment_status,
            'updated_at': s.updated_at.isoformat(),
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([])
def sync_staff(request):
    api_key = _validate_api_key(request)
    if api_key is None:
        return Response({'error': 'Invalid or missing API key'}, status=401)

    updated_since = request.query_params.get('updated_since')
    qs = Staff.objects.all().select_related('department')
    if updated_since:
        qs = qs.filter(updated_at__gte=updated_since)
    data = []
    for s in qs:
        data.append({
            'tsc_number': s.tsc_number,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'department': s.department.name if s.department else None,
            'phone': s.phone,
            'status': s.status,
            'updated_at': s.updated_at.isoformat(),
        })
    return Response(data)

@api_view(['GET'])
@permission_classes([])
def test_connection(request):
    api_key = _validate_api_key(request)
    if api_key is None:
        return Response({'error': 'Invalid or missing API key'}, status=401)
    return Response({'status': 'ok', 'message': 'Connection successful'})

def _validate_api_key(request):
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return None
    try:
        key_obj = APIKey.objects.get(key=api_key, is_active=True)
        if key_obj.expires_at and key_obj.expires_at < timezone.now():
            return None
        key_obj.last_used_at = timezone.now()
        key_obj.save(update_fields=['last_used_at'])
        return key_obj
    except APIKey.DoesNotExist:
        return None


class LostBookEventViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """
    ViewSet for bursar/admin to manage lost book events.
    - List events
    - Retrieve single event
    - Update (PATCH) to set fee_amount, is_cleared, invoice_line_item, etc.
    No delete, no create (creation is done via LMS endpoint).
    """
    queryset = LostBookEvent.objects.all().order_by('-loss_date')
    serializer_class = LostBookEventSerializer
    permission_classes = [IsBursar | IsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get('student')
        if student_id:
            qs = qs.filter(student_id=student_id)
        cleared = self.request.query_params.get('cleared')
        if cleared is not None:
            cleared_bool = cleared.lower() == 'true'
            qs = qs.filter(is_cleared=cleared_bool)
        return qs
    
    def perform_update(self, serializer):
        instance = self.get_object()
        old_cleared = instance.is_cleared
        instance = serializer.save()
        if instance.is_cleared != old_cleared:
            log_custom_action(
                action='CLEAR',
                table_name='integration_lostbookevent',
                record_id=instance.id,
                old_values={'is_cleared': old_cleared},
                new_values={'is_cleared': instance.is_cleared}
            )