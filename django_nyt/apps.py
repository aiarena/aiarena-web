from django.apps import AppConfig


class DjangoNYTConfig(AppConfig):
    name = "django_nyt"
    verbose_name = "Stub django_nyt (temporary)"


# Backwards-compatible alias expected by Django (DjangoNytConfig)
class DjangoNytConfig(DjangoNYTConfig):
    """Alias for DjangoNYTConfig to satisfy Django app-name->AppConfig convention."""

    pass
