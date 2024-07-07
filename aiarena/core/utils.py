import json
import logging
import os
import re
import time
import traceback
from urllib import request

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection

from aiarena.core.s3_helpers import is_s3_file


def obtain_s3_filehash_or_default(file, default):
    """
    Returns the ETAG of the file if it's stored on S3, otherwise returns the default value provided.
    """
    assert file is not None, "file is None"

    # if the file is stored on S3, then return it's ETAG
    if is_s3_file(file):
        path_prefix = file.storage.location
        hash = file.storage.bucket.Object(path_prefix + file.name).e_tag
        return remove_quotes(hash)
    else:
        return default


def remove_quotes(etag):
    # [1:-1] is to remove the quotes from the ETAG
    return etag[1:-1]


logger = logging.getLogger(__name__)


def dictfetchall(cursor) -> list[dict]:
    """
    Returns all rows from a cursor as a dict

    Source: https://docs.djangoproject.com/en/dev/topics/db/sql/#executing-custom-sql-directly
    """
    return [{col[0]: x for col, x in zip(cursor.description, row)} for row in cursor.fetchall()]


def sql(statement, params=()) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(statement, params)
        return dictfetchall(cursor)


def parse_tags(tags):
    """convert tags from single string to list if applicable, and then cleans the tags"""
    if tags:
        if isinstance(tags, str):
            tags = tags.split(",")
        tags = [
            re.sub(settings.MATCH_TAG_REGEX, "", tag.lower().strip())[: settings.MATCH_TAG_LENGTH_LIMIT]
            for tag in tags
            if tag
        ]
        # Remove empty strings that resulted from processing
        return [tag for tag in tags if tag][: settings.MATCH_TAG_PER_MATCH_LIMIT]
    return []


def calculate_md5(file, block_size=2**20):
    """Returns MD% checksum for given file."""
    import hashlib

    md5 = hashlib.md5()

    with open(file, "rb") as file_data:
        while True:
            data = file_data.read(block_size)
            if not data:
                break
            md5.update(data)

    return md5.hexdigest()


def calculate_md5_django_filefield(file, block_size=2**20):
    """Returns MD% checksum for given file."""
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

        json = {  # todo: nested json
            "match_id": result.match.id,
            "round_id": result.match.round_id,
            "bot1": bots[0].name,
            "bot1_id": bots[0].id,
            "bot1_resultant_elo": participants[0].resultant_elo,
            "bot1_elo_change": participants[0].elo_change,
            "bot1_avg_step_time": participants[0].avg_step_time,
            "bot2": bots[1].name,
            "bot2_id": bots[1].id,
            "bot2_resultant_elo": participants[1].resultant_elo,
            "bot2_elo_change": participants[1].elo_change,
            "bot2_avg_step_time": participants[1].avg_step_time,
            "winner": wl_bots[0].name if wl_bots is not None else None,
            "loser": wl_bots[1].name if wl_bots is not None else None,
            "result_type": result.type,
            "game_steps": result.game_steps,
            "replay_file_download_url": result.replay_file.url if result.replay_file else None,
        }
        post_json_content_to_address(json, settings.POST_SUBMITTED_RESULTS_TO_ADDRESS)
    except Exception:
        logger.warning(
            f"Attempt to post result for match_id {result.match.id} to discord failed with error:"
            + os.linesep
            + traceback.format_exc()
        )


def post_json_content_to_address(json_content, address):
    req = request.Request(address)
    req.add_header("Content-Type", "application/json; charset=utf-8")
    jsondata = json.dumps(json_content)
    jsondataasbytes = jsondata.encode("utf-8")  # needs to be bytes
    req.add_header("Content-Length", len(jsondataasbytes))
    print(jsondataasbytes)
    request.urlopen(req, jsondataasbytes)
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


class ReprJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            return repr(o)


def timestamp_ms():
    return int(round(time.time() * 1000))


def monitoring_minute_key(minutes_from_now=0):
    return int(time.time() // 60 + minutes_from_now) * 60
