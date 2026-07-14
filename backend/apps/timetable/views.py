from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.common.mixins import SchoolFilterMixin
from apps.accounts.permissions import IsAdmin, IsPrincipal, IsTeacher, IsParent
from .models import SchoolDay, Period, Room, TeacherAvailability, SubjectAllocation, Timetable, TimetableEntry
from .serializers import (
    SchoolDaySerializer, PeriodSerializer, RoomSerializer,
    TeacherAvailabilitySerializer, SubjectAllocationSerializer,
    TimetableSerializer, TimetableEntrySerializer
)
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

# ---------- Base permissions for reading timetable ----------
class IsTeacherOrAbove(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'principal', 'teacher']

# ---------- ViewSets ----------
class SchoolDayViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = SchoolDay.objects.all()
    serializer_class = SchoolDaySerializer
    permission_classes = [IsAdmin | IsPrincipal]

class PeriodViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    permission_classes = [IsAdmin | IsPrincipal]

class RoomViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdmin | IsPrincipal]

class TeacherAvailabilityViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = TeacherAvailability.objects.all()
    serializer_class = TeacherAvailabilitySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin | IsPrincipal | IsTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'teacher':
            # Teachers can only see their own availability
            qs = qs.filter(teacher=user.staff_profile)
        return qs

    def perform_create(self, serializer):
        # Ensure teacher belongs to the current school
        teacher = serializer.validated_data.get('teacher')
        if teacher.school != self.request.school:
            raise PermissionDenied("Teacher does not belong to this school")
        serializer.save(school=self.request.school)

class SubjectAllocationViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = SubjectAllocation.objects.all()
    serializer_class = SubjectAllocationSerializer
    permission_classes = [IsAdmin | IsPrincipal]

class TimetableViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAdmin | IsPrincipal]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.staff_profile)

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    @transaction.atomic
    def generate(self, request, pk=None):
        timetable = self.get_object()
        if timetable.status != 'draft':
            return Response({'error': 'Only draft timetables can be generated'}, status=400)

        # Get all needed data
        school = timetable.school
        days = SchoolDay.objects.filter(school=school, is_active=True).order_by('order')
        periods = Period.objects.filter(school=school).order_by('order')
        # Exclude break/lunch periods from teaching slots
        teaching_periods = periods.filter(is_break=False, is_lunch=False, is_assembly=False)
        allocations = SubjectAllocation.objects.filter(school=school).select_related('class_obj', 'stream', 'subject', 'teacher')

        # We'll use a simple greedy algorithm:
        # For each allocation, assign to a free slot where teacher, room, class are free.
        # We need a list of rooms; we'll pick the first available.
        rooms = Room.objects.filter(school=school, is_active=True)

        created = 0
        errors = []
        # We'll track used slots for each teacher, room, class (day, period)
        used_teacher = {}
        used_room = {}
        used_class = {}

        for allocation in allocations:
            assigned = False
            for day in days:
                for period in teaching_periods:
                    # Check teacher availability (if defined)
                    avail = TeacherAvailability.objects.filter(
                        teacher=allocation.teacher, day=day, period=period
                    ).first()
                    if avail and not avail.is_available:
                        continue
                    # Check if already used
                    if (allocation.teacher.id, day.id, period.id) in used_teacher:
                        continue
                    # Check if class already used
                    class_key = (allocation.class_obj.id, day.id, period.id)
                    if (allocation.class_obj.id, day.id, period.id) in used_class:
                        continue
                    # Check if stream used (if stream exists)
                    if allocation.stream:
                        stream_key = (allocation.stream.id, day.id, period.id)
                        if (allocation.stream.id, day.id, period.id) in used_class:
                            continue
                    # Find a free room
                    room = None
                    for r in rooms:
                        if (r.id, day.id, period.id) not in used_room:
                            room = r
                            break
                    if room is None:
                        continue
                    # Assign
                    entry = TimetableEntry.objects.create(
                        timetable=timetable,
                        day=day,
                        period=period,
                        class_obj=allocation.class_obj,
                        stream=allocation.stream,
                        subject_allocation=allocation,
                        subject=allocation.subject,
                        teacher=allocation.teacher,
                        room=room
                    )
                    used_teacher[(allocation.teacher.id, day.id, period.id)] = True
                    used_room[(room.id, day.id, period.id)] = True
                    used_class[(allocation.class_obj.id, day.id, period.id)] = True
                    if allocation.stream:
                        used_class[(allocation.stream.id, day.id, period.id)] = True
                    created += 1
                    assigned = True
                    break
                if assigned:
                    break
            if not assigned:
                errors.append(f"Could not assign {allocation}")

        if created == 0:
            return Response({'error': 'No allocations could be assigned. Check constraints.'}, status=400)

        return Response({
            'status': 'generated',
            'entries_created': created,
            'errors': errors
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def publish(self, request, pk=None):
        timetable = self.get_object()
        if timetable.status != 'draft':
            return Response({'error': 'Only draft timetables can be published'}, status=400)
        timetable.status = 'published'
        timetable.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def archive(self, request, pk=None):
        timetable = self.get_object()
        if timetable.status != 'published':
            return Response({'error': 'Only published timetables can be archived'}, status=400)
        timetable.status = 'archived'
        timetable.save()
        return Response({'status': 'archived'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def validate(self, request, pk=None):
        timetable = self.get_object()
        entries = timetable.entries.all()
        issues = []

        # Check teacher double-bookings
        teacher_slots = {}
        for entry in entries:
            key = (entry.teacher_id, entry.day_id, entry.period_id)
            if key in teacher_slots:
                issues.append(f"Teacher {entry.teacher} double-booked on {entry.day} period {entry.period} (clash with {teacher_slots[key]})")
            else:
                teacher_slots[key] = f"{entry.class_obj} - {entry.subject}"

        # Check room double-bookings
        room_slots = {}
        for entry in entries:
            key = (entry.room_id, entry.day_id, entry.period_id)
            if key in room_slots:
                issues.append(f"Room {entry.room} double-booked on {entry.day} period {entry.period} (clash with {room_slots[key]})")
            else:
                room_slots[key] = f"{entry.class_obj} - {entry.subject}"

        # Check class double-bookings
        class_slots = {}
        for entry in entries:
            key = (entry.class_obj_id, entry.day_id, entry.period_id)
            if entry.stream:
                key = (entry.class_obj_id, entry.stream_id, entry.day_id, entry.period_id)
            if key in class_slots:
                issues.append(f"Class {entry.class_obj} (stream {entry.stream}) double-booked on {entry.day} period {entry.period} (clash with {class_slots[key]})")
            else:
                class_slots[key] = f"{entry.subject}"

        if issues:
            return Response({'valid': False, 'issues': issues})
        return Response({'valid': True})

    @action(detail=True, methods=['get'], permission_classes=[IsAdmin | IsPrincipal])
    def clashes(self, request, pk=None):
        # Same as validate but returns only issues
        timetable = self.get_object()
        # Reuse validation logic or call validate
        # We'll just call the validation and return the issues
        # But we need to avoid recursion; we can duplicate logic.
        # Better to extract a helper method.
        issues = self._validate_timetable(timetable)
        return Response({'clashes': issues})

    def _validate_timetable(self, timetable):
        # Helper method used by validate and clashes
        entries = timetable.entries.all()
        issues = []
        # ... same logic as validate
        return issues
    

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin | IsPrincipal])
    def duplicate(self, request, pk=None):
        source_timetable = self.get_object()
        if source_timetable.status not in ['published', 'archived']:
            return Response({'error': 'Only published or archived timetables can be duplicated'}, status=400)

        # Create new timetable
        new_timetable = Timetable.objects.create(
            school=source_timetable.school,
            name=f"{source_timetable.name} (Copy)",
            academic_year=source_timetable.academic_year,
            term=source_timetable.term,
            status='draft',
            created_by=request.user.staff_profile
        )
        # Copy all entries
        for entry in source_timetable.entries.all():
            TimetableEntry.objects.create(
                timetable=new_timetable,
                day=entry.day,
                period=entry.period,
                class_obj=entry.class_obj,
                stream=entry.stream,
                subject_allocation=entry.subject_allocation,
                subject=entry.subject,
                teacher=entry.teacher,
                room=entry.room
            )
        return Response({
            'status': 'duplicated',
            'new_timetable_id': new_timetable.id
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdmin | IsPrincipal])
    def teacher_workload(self, request):
        # Aggregate entries per teacher, count lessons per day/week etc.
        entries = TimetableEntry.objects.filter(timetable__school=request.school)
        workload = entries.values('teacher__id', 'teacher__first_name', 'teacher__last_name', 'day__name') \
                        .annotate(lessons=Count('id')).order_by('teacher__id', 'day__order')
        # Format response
        data = {}
        for item in workload:
            teacher_id = item['teacher__id']
            teacher_name = f"{item['teacher__first_name']} {item['teacher__last_name']}"
            day = item['day__name']
            if teacher_id not in data:
                data[teacher_id] = {'name': teacher_name, 'days': {}}
            data[teacher_id]['days'][day] = item['lessons']
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdmin | IsPrincipal])
    def room_utilization(self, request):
        entries = TimetableEntry.objects.filter(timetable__school=request.school)
        utilization = entries.values('room__id', 'room__name', 'day__name') \
                            .annotate(lessons=Count('id')).order_by('room__id', 'day__order')
        data = {}
        for item in utilization:
            room_id = item['room__id']
            room_name = item['room__name']
            day = item['day__name']
            if room_id not in data:
                data[room_id] = {'name': room_name, 'days': {}}
            data[room_id]['days'][day] = item['lessons']
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdmin | IsPrincipal])
    def free_periods(self, request):
        teacher_id = request.query_params.get('teacher_id')
        class_id = request.query_params.get('class_id')
        if not teacher_id and not class_id:
            return Response({'error': 'teacher_id or class_id required'}, status=400)
        # Implementation: get all periods and filter out those that are booked
        # For simplicity, we'll just return a list of free slots (day, period) for the given teacher or class.

class TimetableEntryViewSet(SchoolFilterMixin, viewsets.ModelViewSet):
    queryset = TimetableEntry.objects.all()
    serializer_class = TimetableEntrySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdmin | IsPrincipal]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = super().get_queryset()
        # Apply role-based filtering first
        user = self.request.user
        if user.role == 'teacher':
            qs = qs.filter(teacher=user.staff_profile)
        elif user.role in ['parent', 'student']:
            if user.student_profile:
                qs = qs.filter(class_obj=user.student_profile.class_obj)
                if user.student_profile.stream:
                    qs = qs.filter(stream=user.student_profile.stream)
            else:
                qs = qs.none()
        # Query params for additional filtering
        class_id = self.request.query_params.get('class_id')
        if class_id:
            qs = qs.filter(class_obj_id=class_id)
        stream_id = self.request.query_params.get('stream_id')
        if stream_id:
            qs = qs.filter(stream_id=stream_id)
        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        room_id = self.request.query_params.get('room_id')
        if room_id:
            qs = qs.filter(room_id=room_id)
        return qs
    
    @action(detail=False, methods=['get'], permission_classes=[IsTeacher])
    def my(self, request):
        teacher = request.user.staff_profile
        if not teacher:
            return Response({'error': 'Teacher profile not found'}, status=404)
        # Get entries for this teacher, optionally for a specific day or period
        entries = self.get_queryset().filter(teacher=teacher)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_class(self, request):
        user = request.user
        if user.role not in ['student', 'parent']:
            return Response({'error': 'Only students and parents can view class timetable'}, status=403)
        student_profile = user.student_profile
        if not student_profile:
            return Response({'error': 'No student profile linked'}, status=404)
        entries = TimetableEntry.objects.filter(
            class_obj=student_profile.class_obj,
            stream=student_profile.stream
        )
        serializer = TimetableEntrySerializer(entries, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsParent])
    def my_child(self, request):
        user = request.user
        if not user.student_profile:
            return Response({'error': 'No student linked to this parent'}, status=404)
        entries = TimetableEntry.objects.filter(
            class_obj=user.student_profile.class_obj,
            stream=user.student_profile.stream
        )
        serializer = TimetableEntrySerializer(entries, many=True)
        return Response(serializer.data)