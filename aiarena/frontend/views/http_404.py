from aiarena.frontend.views import frontend

def react_404(request, exception):
    response = frontend(request)
    response.status_code = 404
    return response