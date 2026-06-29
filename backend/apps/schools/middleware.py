from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from .models import School
import threading

_thread_local = threading.local()

def get_current_school():
    return getattr(_thread_local, 'school', None)

class SchoolMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 1. Check header first (for testing)
        school_id = request.headers.get('X-School-ID')
        if school_id:
            try:
                school = School.objects.get(id=school_id, is_active=True)
                request.school = school
                _thread_local.school = school
                return
            except School.DoesNotExist:
                pass

        # 2. Then check subdomain
        host = request.get_host()
        subdomain = host.split('.')[0] if '.' in host else None
        if subdomain and subdomain not in ['www', 'api', 'admin', 'localhost', '127.0.0.1']:
            try:
                school = School.objects.get(subdomain=subdomain, is_active=True)
                request.school = school
                _thread_local.school = school
            except School.DoesNotExist:
                request.school = None
                _thread_local.school = None
        else:
            request.school = None
            _thread_local.school = None

    def process_response(self, request, response):
        _thread_local.school = None
        return response