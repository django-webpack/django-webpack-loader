def is_first_visit(request):
    return len(request.COOKIES) == 0
