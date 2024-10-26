from django.http import HttpResponse
from django_ratelimit.core import is_ratelimited

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Apply rate limit only to POST requests for the CommentsCreateApiView
        if request.path == "/comments/" and request.method == "POST":
            # Set a unique `group` identifier for this rate limit check
            is_limited = is_ratelimited(
                request, group="comment_create_rate_limit", key="ip", rate="20/m", method="POST", increment=True
            )
            if is_limited:
                # Block and return a 429 error if rate-limited
                return HttpResponse("Rate limit exceeded. Please try again later.", status=429)

        response = self.get_response(request)
        return response