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


validate_bot_name = RegexValidator(r'^[0-9a-zA-Z\._\-]*$',
                                   'Only alphanumeric (A-Z, a-z, 0-9), period (.), underscore (_) '
                                   'and hyphen (-) characters are allowed.')


def validate_bot_zip_file(value):
    try:
        with ZipFile(value.open()) as zip_file:
            expected_name = value.instance.expected_executable_filename()
            if expected_name not in zip_file.namelist():
                raise ValidationError(f"Incorrect bot zip file structure. A bot of type {value.instance.type} "
                                      f"would need to have a file in the zip file root named {expected_name}")
    except BadZipFile:
        raise ValidationError("Bot zip must be a valid zip file")

    return value
