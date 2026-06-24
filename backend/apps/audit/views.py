from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.accounts.permissions import IsAdmin, IsPrincipal, IsBursar
from .utils import generate_pdf_report, generate_excel_report, generate_csv_report   # reuse reporting utils

# ---------- Table to Module mapping ----------
TABLE_TO_MODULE = {
    'auth_user': 'AUTHENTICATION',
    'core_student': 'STUDENTS',
    'core_staff': 'STAFF',
    'academics_class': 'ACADEMICS',
    'academics_stream': 'ACADEMICS',
    'academics_subject': 'ACADEMICS',
    'academics_academicyear': 'ACADEMICS',
    'academics_term': 'ACADEMICS',
    'finance_feeinvoice': 'FINANCE',
    'finance_payment': 'FINANCE',
    'finance_expense': 'FINANCE',
    'finance_paymentallocation': 'FINANCE',
    'payroll_salarystructure': 'PAYROLL',
    'payroll_payrollrun': 'PAYROLL',
    'payroll_payrollentry': 'PAYROLL',
    'payroll_payrollpaymentlog': 'PAYROLL',
    'budget_budgetperiod': 'BUDGET',
    'budget_budgetcategory': 'BUDGET',
    'budget_budgetlineitem': 'BUDGET',
    'integration_apikey': 'INTEGRATION',
    'integration_lostbookevent': 'INTEGRATION',
}

def get_module(table_name):
    return TABLE_TO_MODULE.get(table_name, 'OTHER')

# ---------- Role-based allowed modules ----------
ROLE_MODULES = {
    'admin': set(TABLE_TO_MODULE.values()),  # all
    'principal': {'STUDENTS', 'STAFF', 'ACADEMICS', 'FINANCE', 'PAYROLL', 'BUDGET'},
    'bursar': {'FINANCE', 'PAYROLL', 'BUDGET'},
    'teacher': set(),  # will be implemented later for own activities
    'parent': set(),
}

# ---------- Views ----------
class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'table_name', 'user__username', 'user_role']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        school = getattr(self.request, 'school', None)
        qs = AuditLog.objects.all()

        # If no school in request, return empty (prevent cross‑tenant leakage)
        if not school:
            return qs.none()

        # Filter by school
        qs = qs.filter(school=school)

        # Apply role‑based restrictions
        if user.role == 'admin':
            return qs
        elif user.role == 'principal':
            allowed_modules = ROLE_MODULES.get('principal', set())
            allowed_tables = [t for t, mod in TABLE_TO_MODULE.items() if mod in allowed_modules]
            return qs.filter(table_name__in=allowed_tables)
        elif user.role == 'bursar':
            allowed_modules = ROLE_MODULES.get('bursar', set())
            allowed_tables = [t for t, mod in TABLE_TO_MODULE.items() if mod in allowed_modules]
            return qs.filter(table_name__in=allowed_tables)
        else:
            return qs.none()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AuditLogDetailView(generics.RetrieveAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == 'admin':
            return qs
        allowed_modules = ROLE_MODULES.get(user.role, set())
        allowed_tables = [t for t, mod in TABLE_TO_MODULE.items() if mod in allowed_modules]
        if allowed_tables:
            return qs.filter(table_name__in=allowed_tables)
        return qs.none()


class AuditLogExportView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin | IsPrincipal]   # only admin and principal can export

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return AuditLog.objects.all()
        allowed_modules = ROLE_MODULES.get(user.role, set())
        allowed_tables = [t for t, mod in TABLE_TO_MODULE.items() if mod in allowed_modules]
        if allowed_tables:
            return AuditLog.objects.filter(table_name__in=allowed_tables)
        return AuditLog.objects.none()

    def get(self, request, *args, **kwargs):
        export_type = request.query_params.get('export', 'json')
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        headers = ['ID', 'User', 'Role', 'Action', 'Table', 'Record ID', 'Old Values', 'New Values', 'IP', 'Timestamp']
        table_data = []
        for log in data:
            table_data.append([
                log['id'],
                log['user'] if log.get('user') else 'System',
                log.get('user_role', ''),
                log['action'],
                log['table_name'],
                log['record_id'],
                str(log.get('old_values', {})),
                str(log.get('new_values', {})),
                log.get('ip_address', ''),
                log['created_at']
            ])
        if export_type == 'pdf':
            return generate_pdf_report('Audit Logs', headers, table_data, 'audit.pdf')
        elif export_type == 'excel':
            return generate_excel_report('Audit Logs', headers, table_data, 'audit.xlsx')
        elif export_type == 'csv':
            return generate_csv_report(headers, table_data, 'audit.csv')
        else:
            return Response(data)