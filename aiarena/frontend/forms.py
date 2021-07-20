
# Make it so WebsiteUser models are created on user registration instead of plain User models.
from registration.forms import RegistrationForm

from aiarena.core.models import WebsiteUser


class WebsiteUserRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = WebsiteUser
