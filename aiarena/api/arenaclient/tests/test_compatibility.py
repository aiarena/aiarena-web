import io
import json

from django.test import TransactionTestCase

import jsonschema

from aiarena.core.models import User
from aiarena.core.tests.test_mixins import MatchReadyMixin


class ArenaClientCompatibilityTestCase(MatchReadyMixin, TransactionTestCase):
    """
    This test ensures that the Arena Client endpoint doesn't inadvertently change.

    IF THIS TEST FAILS, YOU MIGHT HAVE BROKEN COMPATIBILITY WITH THE ARENA CLIENT
    """

    def setUp(self):
        super().setUp()
        self.client.force_login(User.objects.get(username="arenaclient1"))

    def validateJson_bySchema(self, jsonData, json_schema) -> (bool, jsonschema.exceptions.ValidationError):
        try:
            jsonschema.validate(instance=jsonData, schema=json_schema)
        except jsonschema.exceptions.ValidationError as error:
            return False, error
        return True, None

    v1_expected_json_schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["id"],
        "properties": {
            "id": {"type": "number"},
            "bot1": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "id",
                    "name",
                    "game_display_id",
                    "bot_zip",
                    "bot_zip_md5hash",
                    "bot_data",
                    "bot_data_md5hash",
                    "plays_race",
                    "type",
                ],
                "properties": {
                    "id": {"type": "number"},
                    "name": {"type": "string"},
                    "game_display_id": {"type": "string"},
                    "bot_zip": {"type": "string"},
                    "bot_zip_md5hash": {"type": "string"},
                    "bot_data": {"type": "string"},
                    "bot_data_md5hash": {"type": "string"},
                    "plays_race": {"type": "string"},
                    "type": {"type": "string"},
                },
            },
            "bot2": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "id",
                    "name",
                    "game_display_id",
                    "bot_zip",
                    "bot_zip_md5hash",
                    "bot_data",
                    "bot_data_md5hash",
                    "plays_race",
                    "type",
                ],
                "properties": {
                    "id": {"type": "number"},
                    "name": {"type": "string"},
                    "game_display_id": {"type": "string"},
                    "bot_zip": {"type": "string"},
                    "bot_zip_md5hash": {"type": "string"},
                    "bot_data": {"type": "string"},
                    "bot_data_md5hash": {"type": "string"},
                    "plays_race": {"type": "string"},
                    "type": {"type": "string"},
                },
            },
            "map": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "name", "file", "enabled", "game_mode", "competitions"],
                "properties": {
                    "id": {"type": "number"},
                    "name": {"type": "string"},
                    "file": {"type": "string"},
                    "enabled": {"type": "boolean"},
                    "game_mode": {"type": "number"},
                    "competitions": {"type": "array"},
                },
            },
        },
    }

    def test_default_version_endpoint_contract(self):
        api_version = None  # should default to v1
        self._test_endpoint_contract(api_version, ArenaClientCompatibilityTestCase.v1_expected_json_schema)

    def test_v1_version_endpoint_contract(self):
        api_version = "v1"
        self._test_endpoint_contract(api_version, ArenaClientCompatibilityTestCase.v1_expected_json_schema)

    def test_v2_version_endpoint_contract(self):
        api_version = "v2"
        expected_json_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["id"],
            "properties": {
                "id": {"type": "number"},
                "bot1": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "name",
                        "game_display_id",
                        "bot_zip",
                        "bot_zip_md5hash",
                        "bot_data",
                        "bot_data_md5hash",
                        "plays_race",
                        "type",
                    ],
                    "properties": {
                        "id": {"type": "number"},
                        "name": {"type": "string"},
                        "game_display_id": {"type": "string"},
                        "bot_zip": {"type": "string"},
                        "bot_zip_md5hash": {"type": "string"},
                        "bot_data": {"type": "string"},
                        "bot_data_md5hash": {"type": "string"},
                        "plays_race": {"type": "string"},
                        "type": {"type": "string"},
                    },
                },
                "bot2": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "name",
                        "game_display_id",
                        "bot_zip",
                        "bot_zip_md5hash",
                        "bot_data",
                        "bot_data_md5hash",
                        "plays_race",
                        "type",
                    ],
                    "properties": {
                        "id": {"type": "number"},
                        "name": {"type": "string"},
                        "game_display_id": {"type": "string"},
                        "bot_zip": {"type": "string"},
                        "bot_zip_md5hash": {"type": "string"},
                        "bot_data": {"type": "string"},
                        "bot_data_md5hash": {"type": "string"},
                        "plays_race": {"type": "string"},
                        "type": {"type": "string"},
                    },
                },
                "map": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["name", "file"],
                    "properties": {
                        "name": {"type": "string"},
                        "file": {"type": "string"},
                        "file_hash": {"type": ["string", "null"]},
                    },
                },
            },
        }
        self._test_endpoint_contract(api_version, expected_json_schema)

    def test_v3_version_endpoint_contract(self):
        api_version = "v3"
        expected_json_schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["id"],
            "properties": {
                "id": {"type": "number"},
                "bot1": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "name",
                        "game_display_id",
                        "bot_zip",
                        "bot_zip_md5hash",
                        "bot_data",
                        "bot_data_md5hash",
                        "plays_race",
                        "type",
                    ],
                    "properties": {
                        "id": {"type": "number"},
                        "name": {"type": "string"},
                        "game_display_id": {"type": "string"},
                        "bot_zip": {"type": "string"},
                        "bot_zip_md5hash": {"type": "string"},
                        "bot_data": {"type": "string"},
                        "bot_data_md5hash": {"type": "string"},
                        "plays_race": {"type": "string"},
                        "type": {"type": "string"},
                    },
                },
                "bot2": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "name",
                        "game_display_id",
                        "bot_zip",
                        "bot_zip_md5hash",
                        "bot_data",
                        "bot_data_md5hash",
                        "plays_race",
                        "type",
                    ],
                    "properties": {
                        "id": {"type": "number"},
                        "name": {"type": "string"},
                        "game_display_id": {"type": "string"},
                        "bot_zip": {"type": "string"},
                        "bot_zip_md5hash": {"type": "string"},
                        "bot_data": {"type": "string"},
                        "bot_data_md5hash": {"type": "string"},
                        "plays_race": {"type": "string"},
                        "type": {"type": "string"},
                    },
                },
                "map": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["name", "file"],
                    "properties": {
                        "name": {"type": "string"},
                        "file": {"type": "string"},
                        "file_hash": {"type": ["string", "null"]},
                    },
                },
            },
        }
        self._test_endpoint_contract(api_version, expected_json_schema)

    def _test_endpoint_contract(self, version, expected_json_schema):
        response = self._post_to_matches(version)
        validation_successful, error = self.validateJson_bySchema(
            json.load(io.BytesIO(response.content)), expected_json_schema
        )
        if not validation_successful:
            raise Exception(
                f"The AC API {version} next match endpoint json schema has changed! "
                "If you intentionally changed it, update this test and the arenaclient.\n"
                "ValidationError:\n" + str(error)
            )
