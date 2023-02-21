import hashlib
import json
import logging
import os
import random
import shutil
from urllib import parse

import requests

logger = logging.getLogger(__name__)


class AiArenaWebACApi:
    """
    An interface to the live AI Arena website ArenaClient API
    """
    API_MATCHES_ENDPOINT = "/api/arenaclient/matches/"
    API_RESULTS_ENDPOINT = "/api/arenaclient/results/"

    def __init__(self, ac_id, api_url, api_token):
        self._ac_id = ac_id
        self.API_URL = api_url
        self.API_TOKEN = api_token
        self.API_MATCHES_URL = parse.urljoin(self.API_URL, AiArenaWebACApi.API_MATCHES_ENDPOINT)
        self.API_RESULTS_URL = parse.urljoin(self.API_URL, AiArenaWebACApi.API_RESULTS_ENDPOINT)

    def get_match(self):
        """
        Gets the next match in queue
        """
        try:
            next_match_response = requests.post(
                self.API_MATCHES_URL,
                headers={"Authorization": "Token " + self.API_TOKEN},
            )
        except ConnectionError:
            logger.error(f"AC {self._ac_id}: Failed to retrieve game. Connection to website failed.")
            return None

        if next_match_response.status_code >= 400:
            if next_match_response.status_code >= 500:
                # scheduling related functionality
                logger.info(f"AC {self._ac_id}: Failed to retrieve game. Status code: {next_match_response.status_code}.")
            else:
                logger.error(f"AC {self._ac_id}: Failed to retrieve game. Status code: {next_match_response.status_code}.")
            return None

        return json.loads(next_match_response.text)

    def submit_result(self, payload: dict,
                      bot1_data_file_stream, bot2_data_file_stream,
                      bot1_log_file_stream, bot2_log_file_stream,
                      arenaclient_log_zip_file_stream, replay_file_stream=None):
        """
        Submits the supplied result to the AI Arena website API
        """

        file_list = {
            "bot1_data": bot1_data_file_stream,
            "bot2_data": bot2_data_file_stream,
            "bot1_log": bot1_log_file_stream,
            "bot2_log": bot2_log_file_stream,
            "arenaclient_log": arenaclient_log_zip_file_stream,
        }

        if replay_file_stream:
             file_list["replay_file"] = replay_file_stream

        post = requests.post(
            self.API_RESULTS_URL,
            files=file_list,
            data=payload,
            headers={"Authorization": "Token " + self.API_TOKEN},
        )
        return post

    def download_map(self, map_url: str, to_path: str) -> bool:
        success = False
        try:
            r = requests.get(map_url)

            with open(to_path, "wb") as map_file:
                map_file.write(r.content)

            success = True
        except Exception as download_exception:
            logger.error(f"AC {self._ac_id}:Failed to download map at URL {map_url}. Error {download_exception}.")

        return success

    def download_bot_zip(self, bot_zip_url: str, to_path: str):
        r = requests.get(
            bot_zip_url, headers={"Authorization": "Token " + self.API_TOKEN}
        )
        with open(to_path, "wb") as bot_zip:
            bot_zip.write(r.content)

    def download_bot_data(self, bot_data_url: str, to_path: str):
        r = requests.get(
            bot_data_url, headers={"Authorization": "Token " + self.API_TOKEN}
        )
        with open(to_path, "wb") as bot_data_zip:
            bot_data_zip.write(r.content)


class MockArenaClient:
    def __init__(self, ac_id: str, webserver_url: str, api_token: str, working_dir: str):
        self._ac_id = ac_id
        self._webserver_url = webserver_url
        self._api = AiArenaWebACApi(self._ac_id, webserver_url, api_token)
        self._working_dir = working_dir

    def run_matches(self, num_matches: int):
        for x in range(num_matches):
            logger.info(f"AC {self._ac_id}: Running match {x+1} of {num_matches}")
            self.run_a_match()

    def run_a_match(self) -> bool:
        if not os.path.exists(self._working_dir):
            os.makedirs(self._working_dir)

        match = self._api.get_match()

        if match is None:
            logger.info(f"AC {self._ac_id}: New match was none!")
            return False

        if "id" not in match:
            logger.info(f"AC {self._ac_id}: New match ID was missing!")
            return False

        logger.info(f"AC {self._ac_id}: Cleaning working directory {self._working_dir}")
        self._clean_working_dir()

        next_match_id = match["id"]
        logger.info(f"AC {self._ac_id}: Next match: {next_match_id}")

        # Download map
        logger.info(f"AC {self._ac_id}: Downloading map {match['map']['name']}")
        map_path = os.path.join(self._working_dir, f"map.SC2Map")
        if not self._api.download_map(match["map"]["file"], map_path):
            logger.error(f"AC {self._ac_id}: Map download failed.")
            return False

        if not self._download_bots_files(match):
            logger.error(f"AC {self._ac_id}: Failed to download bot files.")
            return False

        result = self._mock_match_activity()
        return self._submit_result(match, result, random.randint(1, 80640))

    def _clean_working_dir(self):
        # Iterate over the files in the folder and delete them
        for filename in os.listdir(self._working_dir):
            file_path = os.path.join(self._working_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    # Use shutil.rmtree to remove subdirectories and their contents
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"AC {self._ac_id}: Failed to delete {file_path}. Reason: {e}")

    def _download_bots_files(self, match: dict):
        return self._download_bot_files(match["bot1"], "1") \
            and self._download_bot_files(match["bot2"], "2")

    def _mock_match_activity(self) -> str:
        # todo: determine result
        # todo: log stuff to bot data & AC log

        # Create a fake replay file
        with open(os.path.join(self._working_dir, "replay.SC2Replay"), 'wt') as f:
            f.write("This is a mock replay")

        return "Tie"

    def _submit_result(self, match, result_type, game_steps):
        success = True

        bot1_data = self._open_if_present("bot1-data.zip")
        bot1_log = self._open_if_present("bot1-log.zip")

        bot2_data = self._open_if_present("bot2-data.zip")
        bot2_log = self._open_if_present("bot2-log.zip")

        arenaclient_log = self._open_if_present("ac-log.zip")

        replay_file_stream = self._open_if_present("replay.SC2Replay")

        payload = {"type": result_type, "match": int(match["id"]), "game_steps": game_steps}

        # if result.bot1_avg_frame is not None:
        #     payload["bot1_avg_step_time"] = result.bot1_avg_frame
        # if result.bot2_avg_frame is not None:
        #     payload["bot2_avg_step_time"] = result.bot2_avg_frame
        #
        # if result.bot1_tags is not None:
        #     payload["bot1_tags"] = result.bot1_tags
        #
        # if result.bot2_tags is not None:
        #     payload["bot2_tags"] = result.bot2_tags

        post = self._api.submit_result(payload,
                                       bot1_data, bot2_data,
                                       bot1_log, bot2_log,
                                       arenaclient_log, replay_file_stream)

        if post is None:
            success = False
            logger.error(f"AC {self._ac_id}: Result submission failed. 'post' was None.")
        elif post.status_code >= 400:
            success = False
            logger.error(f"AC {self._ac_id}: Result submission failed. Status code: {post.status_code}.")
        else:
            logger.info(f"AC {self._ac_id}: {result_type} - Result transferred")

        def close(f):
            if f:
                f.close()

        close(bot1_data)
        close(bot1_log)
        close(bot2_data)
        close(bot2_log)
        close(arenaclient_log)
        close(replay_file_stream)

        return success

    def _open_if_present(self, file_name):
        path = os.path.join(self._working_dir, file_name)
        file_data = None
        if os.path.isfile(path):
            file_data = open(path, "rb")
        return file_data

    def _download_bot_files(self, bot: dict, bot_num: str):
        return self._download_bot_zip(bot, bot_num) and self._download_bot_data(bot, bot_num)

    def _download_bot_zip(self, bot: dict, bot_num: str):
        bot_download_path = os.path.join(self._working_dir, f"bot{bot_num}.zip")
        self._api.download_bot_zip(bot["bot_zip"], bot_download_path)

        # Load bot from .zip to calculate md5
        with open(bot_download_path, "rb") as bot_zip:
            calculated_md5 = hashlib.md5(self.file_as_bytes(bot_zip)).hexdigest()
        if not bot["bot_zip_md5hash"] == calculated_md5:
            logger.error(f"MD5 hash ({bot['bot_zip_md5hash']}) does not match transferred file ({calculated_md5})")
            return False
        return True

    def _download_bot_data(self, bot: dict, bot_num: str):
        if bot["bot_data"] is None:
            return True
        bot_data_path = os.path.join(self._working_dir, f"bot{bot_num}-data.zip")
        self._api.download_bot_data(bot["bot_data"], bot_data_path)
        with open(bot_data_path, "rb") as bot_data_zip:
            calculated_md5 = hashlib.md5(self.file_as_bytes(bot_data_zip)).hexdigest()

            if not bot["bot_data_md5hash"] == calculated_md5:
                logger.error(f"AC {self._ac_id}: MD5 hash ({bot['bot_zip_md5hash']}) does not match transferred file ({calculated_md5})")
                return False
        return True

    @staticmethod
    def file_as_bytes(file):
        with file:
            return file.read()
