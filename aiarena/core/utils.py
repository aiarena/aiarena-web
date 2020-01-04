import json
import logging
import os
import traceback
from urllib import request
from enum import Enum
from zipfile import ZipFile

from aiarena import settings

logger = logging.getLogger(__name__)

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
        participants = result.get_match_participants()
        bots = result.get_match_participant_bots()

        if result.has_winner():
            wl_bots = result.get_winner_loser_bots()
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

def add_result_replay_file_to_season_archive(result):
    """
    If there's a replay file, add it to the season's replay archive
    :param result:
    :return:
    """
    try:
        if result.replay_file:
            with ZipFile(result.match.round.season.replay_archive_zip.file.name, "a") as zip_file:
                file_path = result.replay_file.file.name
                zip_file.write(file_path, arcname=os.path.basename(file_path))
    except Exception as e:
        logger.error(f"Attempt to add replay file for result of match_id {result.match_id} to season archive failed with error:"
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
