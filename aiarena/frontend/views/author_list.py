from django.views.generic import ListView

from aiarena.core.models import User


class AuthorList(ListView):
    queryset = User.objects.filter(is_active=1, type="WEBSITE_USER").order_by("username")
    template_name = "authors.html"
