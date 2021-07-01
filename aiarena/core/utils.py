import re
import json
import logging
import os
import traceback
from urllib import request
from enum import Enum
from zipfile import ZipFile
from django.db.models.fields import CharField
from django.db.models import Q, Aggregate, CharField
from rest_framework.exceptions import ValidationError

from aiarena import settings

logger = logging.getLogger(__name__)


class GroupConcat(Aggregate):
    function = 'GROUP_CONCAT'
    template = '%(function)s(%(distinct)s%(expressions)s%(ordering)s%(separator)s)'

    def __init__(self, expression, distinct=False, ordering=None, separator=',', **extra):
        super(GroupConcat, self).__init__(
            expression,
            distinct='DISTINCT ' if distinct else '',
            ordering=' ORDER BY %s' % ordering if ordering is not None else '',
            separator=' SEPARATOR "%s"' % separator,
            output_field=CharField(),
            **extra
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
    if '|' in value:
        users_str, tags_str = [s.strip() for s in value.split('|')]
    else:
        users_str = ""
        tags_str = value

    method = lambda q: q.filter if not exclude else q.exclude

    if user_field_name and users_str:
        try:
            users = [int(s) for s in users_str.split(',')]
        except ValueError:
            raise ValidationError({"tags":["When using pipe separator (|), Expecting user_id (int) on LHS and tag_name on RHS of separator."]})
    else:
        users = []

    # Build query for users
    user_query = Q()
    user_lookup = '%s__%s' % (user_field_name, 'exact')
    for v in users:
        user_query |= Q(**{user_lookup: v})

    # Build query for tags
    tag_query = Q()
    if tags_str:
        tags = [s.strip() for s in tags_str.split(',')]
        tags = [s for s in tags if s]
        if tags_lookup_expr == 'icontains':
            qs = method(qs)(user_query).distinct()
            # Create string with all tag names and run icontains on the string
            qs = qs.annotate(all_tags=GroupConcat(tags_field_name))
            tags_lookup = '%s__%s' % ('all_tags', tags_lookup_expr)
            for v in tags:
                tag_query &= Q(**{tags_lookup: v})
            return method(qs)(tag_query)
        else:
            user_lookup = '%s__%s' % (user_field_name, "in")
            tags_lookup = '%s__%s' % (tags_field_name, tags_lookup_expr)
            for v in tags:
                if users:
                    qs = qs.filter(**{tags_lookup: v, user_lookup:users})
                else:
                    qs = qs.filter(**{tags_lookup: v})
            return qs.distinct()

    return method(qs)(user_query).distinct()


def parse_tags(tags):
    """convert tags from single string to list if applicable, and then cleans the tags"""
    if tags:
        if isinstance(tags, str):
            tags = tags.split(",")
        tags = [re.sub(settings.MATCH_TAG_REGEX, '', tag.lower().strip())[:settings.MATCH_TAG_LENGTH_LIMIT] for tag in tags if tag]
        # Remove empty strings that resulted from processing
        return [tag for tag in tags if tag][:settings.MATCH_TAG_PER_MATCH_LIMIT]
    return []


def calculate_md5(file, block_size=2 ** 20):
    """Returns MD% checksum for given file.
    """
    import hashlib

    md5 = hashlib.md5()

    with open(file, 'rb') as file_data:
        while True:
            data = file_data.read(block_size)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


def calculate_md5_django_filefield(file, block_size=2 ** 20):
    """Returns MD% checksum for given file.
    """
    import hashlib

    md5 = hashlib.md5()

    with file.open() as file_stream:
        while True:
            data = file_stream.read(block_size)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


def post_result_to_discord_bot(result):
    try:
        participants = result.get_match_participants
        bots = result.get_match_participant_bots

        if result.has_winner:
            wl_bots = result.get_winner_loser_bots
        else:
            wl_bots = None

        json = { # todo: nested json
            'match_id': result.match_id,
            'round_id': result.match.round_id,
            'bot1': bots[0].name,
            'bot1_id': bots[0].id,
            'bot1_resultant_elo': participants[0].resultant_elo,
            'bot1_elo_change': participants[0].elo_change,
            'bot1_avg_step_time': participants[0].avg_step_time,
            'bot2': bots[1].name,
            'bot2_id': bots[1].id,
            'bot2_resultant_elo': participants[1].resultant_elo,
            'bot2_elo_change': participants[1].elo_change,
            'bot2_avg_step_time': participants[1].avg_step_time,
            'winner': wl_bots[0].name if wl_bots is not None else None,
            'loser': wl_bots[1].name if wl_bots is not None else None,
            'result_type': result.type,
            'game_steps': result.game_steps,
            'replay_file_download_url': result.replay_file.url if result.replay_file else None}
        post_json_content_to_address(json, settings.POST_SUBMITTED_RESULTS_TO_ADDRESS)
    except Exception as e:
        logger.warning(f"Attempt to post result for match_id {result.match_id} to discord failed with error:"
                       + os.linesep + traceback.format_exc())

def post_json_content_to_address(json_content, address):
    req = request.Request(address)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsondata = json.dumps(json_content)
    jsondataasbytes = jsondata.encode('utf-8')  # needs to be bytes
    req.add_header('Content-Length', len(jsondataasbytes))
    print(jsondataasbytes)
    response = request.urlopen(req, jsondataasbytes)
    # todo: check response

# ELO Implementation:
# http://satirist.org/ai/starcraft/blog/archives/117-Elo-ratings-are-easy-to-calculate.html
class Elo:
    def __init__(self, elo_k):
        self.elo_k = elo_k

    # winIndicator:
    # 1.0 = rating1 won
    # 0.0 = rating2 won
    # 0.5 = draw
    def calculate_elo_delta(self, rating1, rating2, winIndicator):
        return self.elo_k * (winIndicator - self.calculate_elo_expected_win_rate(rating1, rating2))

    def calculate_elo_expected_win_rate(self, rating1, rating2):
        return 1.0 / (1.0 + 10.0 ** ((rating2 - rating1) / 400.0))


class EnvironmentType(Enum):
    DEVELOPMENT = 1
    PRODUCTION = 2
    STAGING = 3
