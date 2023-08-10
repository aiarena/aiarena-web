import math
from zipfile import ZipFile, BadZipFile

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_not_nan(value):
    if math.isnan(value):
        raise ValidationError("Value cannot be nan")
    return value


def validate_not_inf(value):
    if math.isinf(value):
        raise ValidationError("Value cannot be inf")
    return value

#  Kept for the migrations not to break.
def validate_user_owner(value):
    pass


validate_bot_name = RegexValidator(r'^[0-9a-zA-Z\._\-]*$',
                                   'Only alphanumeric (A-Z, a-z, 0-9), period (.), underscore (_) '
                                   'and hyphen (-) characters are allowed.')


def validate_bot_zip_file(value):
    pass
