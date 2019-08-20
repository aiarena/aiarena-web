import math

from django.core.exceptions import ValidationError


def validate_not_nan(value):
    if math.isnan(value):
        raise ValidationError("Value cannot be nan")
    return value


def validate_not_inf(value):
    if math.isinf(value):
        raise ValidationError("Value cannot be inf")
    return value
