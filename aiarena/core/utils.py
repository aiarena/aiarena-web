import json
from urllib import request
from enum import Enum

from aiarena import settings


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
    if settings.POST_SUBMITTED_RESULTS_TO_ADDRESS:
        try:
            participants = result.get_participants()
            bots = result.get_participant_bots()
            wl_bots = result.get_winner_loser_bots()
            json = { # todo: nested json
                'match_id': result.match_id,
                'bot1': bots[0].name,
                'bot1_resultant_elo': participants[0].resultant_elo,
                'bot1_elo_change': participants[0].elo_change,
                'bot1_avg_step_time': participants[0].avg_step_time,
                'bot2': bots[1].name,
                'bot2_resultant_elo': participants[1].resultant_elo,
                'bot2_elo_change': participants[1].elo_change,
                'bot2_avg_step_time': participants[1].avg_step_time,
                'winner': wl_bots[0].name,
                'loser': wl_bots[1].name,
                'result_type': result.type,
                'game_steps': result.game_steps,
                'replay_file_download_url': result.replay_file.url}
            post_json_content_to_address(json, settings.POST_SUBMITTED_RESULTS_TO_ADDRESS)
        except Exception as e:
            pass  # todo: log warning if this fails

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
