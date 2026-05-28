from django.urls import path, include


urlpatterns = [
    path('accounts/', include('apps.accounts.urls')),
    path('finance/', include('apps.finance.urls')),
]