from django.urls import path, include


urlpatterns = [
    path('accounts/', include('apps.accounts.urls')),
    path('finance/', include('apps.finance.urls')),
    path('payroll/', include('apps.payroll.urls')),
    path('budget/', include('apps.budget.urls')),
    path('integration/', include('apps.integration.urls')),
    path('reports/', include('apps.reporting.urls')),
    path('audit/', include('apps.audit.urls')),
    path('core/', include('apps.core.urls')),
    path('schools/', include('apps.schools.urls')),
    path('academics/', include('apps.academics.urls')),
]