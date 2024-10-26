from django.http import HttpResponse
from django_ratelimit.core import is_ratelimited

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define rate limits for each path
        path_limits = {
            "/comments/": {"rate": "30/m", "group": "comment_create_rate_limit"},
            "/auth/login/": {"rate": "10/m", "group": "login_rate_limit"},
        }

        # Check if the request path matches any specified paths
        if request.path in path_limits and request.method == "POST":
            limit = path_limits[request.path]
            is_limited = is_ratelimited(
                request,
                group=limit["group"],
                key="ip",
                rate=limit["rate"],
                method="POST",
                increment=True
            )
            if is_limited:
                return HttpResponse("Rate limit exceeded. Please try again later.", status=429)

        # Proceed to the next middleware or view
        response = self.get_response(request)
        return response