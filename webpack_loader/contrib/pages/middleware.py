from django.utils.deprecation import MiddlewareMixin


# noinspection PyMethodMayBeStatic
class FirstVisitMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.first_visit = len(request.COOKIES) == 0
