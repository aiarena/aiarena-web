from typing import List

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APIClient

from aiarena.core.models import Match, Result
from aiarena.core.tests.testing_utils import TestAssetPaths


class AcApiTestingClient(APIClient):
    def __init__(self, api_token: str = None, **defaults):
        super().__init__(**defaults)

        if api_token:
            self.credentials(HTTP_AUTHORIZATION="Token " + api_token)

    def set_api_token(self, api_token: str):
        self.credentials(HTTP_AUTHORIZATION="Token " + api_token)

    def post_to_matches(self) -> Match:
        url = reverse("ac_next_match-list")
        response = self.post(url)
        return response

    def next_match(self) -> Match:
        response = self.post_to_matches()

        assert response.status_code == 201, f"{response.status_code} {response.data}"
        return Match.objects.get(id=response.data["id"])

    def submit_custom_result(
        self,
        match_id,
        result_type,
        replay_file,
        bot1_data,
        bot2_data,
        bot1_log,
        bot2_log,
        arenaclient_log,
        bot1_tags=None,
        bot2_tags=None,
    ):
        data = {
            "match": match_id,
            "type": result_type,
            "replay_file": replay_file,
            "game_steps": 500,
            "bot1_data": bot1_data,
            "bot2_data": bot2_data,
            "bot1_log": bot1_log,
            "bot2_log": bot2_log,
            "bot1_avg_step_time": 0.2,
            "bot2_avg_step_time": 0.1,
            "arenaclient_log": arenaclient_log,
        }
        if bot1_tags:
            data["bot1_tags"] = bot1_tags
        if bot2_tags:
            data["bot2_tags"] = bot2_tags
        return self.publish_result(data)

    def publish_result(self, data):
        url = reverse("ac_submit_result-list")
        return self.post(url, data=data)

    def submit_result(self, match_id: int, type: str) -> Result:
        with open(TestAssetPaths.test_replay_path, "rb") as replay_file, open(
            TestAssetPaths.test_arenaclient_log_path, "rb"
        ) as arenaclient_log, open(TestAssetPaths.test_bot_datas["bot1"][0]["path"], "rb") as bot1_data, open(
            TestAssetPaths.test_bot_datas["bot2"][0]["path"], "rb"
        ) as bot2_data, open(
            TestAssetPaths.test_bot1_match_log_path, "rb"
        ) as bot1_log, open(
            TestAssetPaths.test_bot2_match_log_path, "rb"
        ) as bot2_log:
            data = {
                "match": match_id,
                "type": type,
                "replay_file": SimpleUploadedFile("replay_file.SC2Replay", replay_file.read()),
                "game_steps": 1344 + (match_id * 5437) % 59400,  # 60 seconds + up to 45 minutes
                "arenaclient_log": SimpleUploadedFile("arenaclient_log.log", arenaclient_log.read()),
                "bot1_data": SimpleUploadedFile("bot1_data.log", bot1_data.read()),
                "bot2_data": SimpleUploadedFile("bot2_data.log", bot2_data.read()),
                "bot1_log": SimpleUploadedFile("bot1_log.log", bot1_log.read()),
                "bot2_log": SimpleUploadedFile("bot2_log.log", bot2_log.read()),
                "bot1_avg_step_time": "0.111",
                "bot2_avg_step_time": "0.222",
            }
            response = self.publish_result(data)

            assert response.status_code == 201, f"{response.status_code} {response.data} {data}"
            return Result.objects.get(id=response.data["result_id"])
