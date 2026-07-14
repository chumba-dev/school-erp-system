import threading
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()
_thread_local = threading.local()

def get_current_user():
    return getattr(_thread_local, 'user', None)

def get_current_ip():
    return getattr(_thread_local, 'ip', None)

class AuditMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        _thread_local.ip = ip

        # Try to extract user from JWT token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                if user_id:
                    user = User.objects.get(id=user_id)
                    _thread_local.user = user
                    print(f"[AuditMiddleware] Authenticated user: {user.username}")
                else:
                    _thread_local.user = None
            except jwt.ExpiredSignatureError:
                print("[AuditMiddleware] Token expired")
                _thread_local.user = None
            except jwt.InvalidTokenError:
                print("[AuditMiddleware] Invalid token")
                _thread_local.user = None
        else:
            # Fallback to request.user (for session-based auth)
            _thread_local.user = getattr(request, 'user', None)

    def process_response(self, request, response):
        # Clean up thread-local
        _thread_local.user = None
        _thread_local.ip = None
        return response