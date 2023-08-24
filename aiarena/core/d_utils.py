import logging

from django.contrib.postgres.aggregates import StringAgg
from django.db.models import Aggregate, Q
from django.db.models.fields import TextField

from rest_framework.exceptions import ValidationError


# File for housing utils that require 'django' or would break CI if placed in utils.py
logger = logging.getLogger(__name__)


class GroupConcat(Aggregate):
    function = "GROUP_CONCAT"
    template = "%(function)s(%(distinct)s%(expressions)s%(ordering)s%(separator)s)"

    def __init__(self, expression, ordering=None, separator=",", **extra):
        super().__init__(
            expression,
            ordering=" ORDER BY %s" % ordering if ordering is not None else "",
            separator=' SEPARATOR "%s"' % separator,
            output_field=TextField(),
            **extra,
        )


def filter_tags(qs, value, tags_field_name, tags_lookup_expr="iexact", user_field_name="", exclude=False):
    """
    Given a string value, filter the queryset for tags found in it.
    qs: queryset
    value: the string to be parsed. If it contains a "|", the LHS of the pipe is treated as users list, RHS as tags, else all are tags.
    """
    if not value:
        return qs

    # Check for pipe separator
    if "|" in value:
        users_str, tags_str = (s.strip() for s in value.split("|"))
    else:
        users_str = ""
        tags_str = value

    method = lambda q: q.filter if not exclude else q.exclude

    if user_field_name and users_str:
        try:
            users = [int(s) for s in users_str.split(",")]
        except ValueError:
            raise ValidationError(
                {
                    "tags": [
                        "When using pipe separator (|), Expecting user_id (int) on LHS and tag_name on RHS of separator."
                    ]
                }
            )
    else:
        users = []

    # Build query for users
    user_query = Q()
    user_lookup = f"{user_field_name}__exact"
    for v in users:
        user_query |= Q(**{user_lookup: v})

    # Build query for tags
    tag_query = Q()
    if tags_str:
        tags = [s.strip() for s in tags_str.split(",")]
        tags = [s for s in tags if s]
        if tags_lookup_expr == "icontains":
            qs = method(qs)(user_query).distinct()
            # Create string with all tag names and run icontains on the string
            qs = qs.annotate(all_tags=StringAgg(tags_field_name, delimiter=","))
            tags_lookup = f"all_tags__{tags_lookup_expr}"
            for v in tags:
                tag_query &= Q(**{tags_lookup: v})
            return method(qs)(tag_query)
        else:
            user_lookup = f"{user_field_name}__in"
            tags_lookup = f"{tags_field_name}__{tags_lookup_expr}"
            for v in tags:
                if users:
                    qs = qs.filter(**{tags_lookup: v, user_lookup: users})
                else:
                    qs = qs.filter(**{tags_lookup: v})
            return qs.distinct()

    return method(qs)(user_query).distinct()
