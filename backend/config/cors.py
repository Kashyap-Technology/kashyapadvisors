from django.conf import settings


class CorsMiddleware:
    """Small dependency-free CORS middleware for the public API."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        origin = request.headers.get('Origin')
        allowed = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if origin in allowed:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, Authorization'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PATCH, DELETE, OPTIONS'
            response['Vary'] = 'Origin'
        return response
