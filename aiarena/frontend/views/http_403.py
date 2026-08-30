from aiarena.frontend.views import frontend

def react_403(request, exception):
    response = frontend(request)
    response.status_code = 403
    return response