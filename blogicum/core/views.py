from django.shortcuts import render


def csrf_failure(request):
    return render(request, 'pages/403csrf.html')

def page_not_found(request, exeption):    
    return render(request, 'pages/404.html', status=404)

def server_error(request, exeption=None):
    return render(request, 'pages/500.html', status=500)