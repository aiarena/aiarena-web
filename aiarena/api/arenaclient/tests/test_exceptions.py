from types import SimpleNamespace
from typing import cast

import pytest
from rest_framework.response import Response
from rest_framework.views import exception_handler

from aiarena.api.arenaclient.common.exceptions import ResultSubmissionConflict
from aiarena.api.arenaclient.common.result_submission_handler import ResultSubmission, submit_result


def test_result_submission_conflict_returns_http_409() -> None:
    bot = SimpleNamespace(name="finished-bot", is_in_match=lambda match_id: False)
    submission = cast(
        ResultSubmission,
        SimpleNamespace(
            match=SimpleNamespace(id=42),
            p1_instance=SimpleNamespace(bot=bot),
        ),
    )

    with pytest.raises(ResultSubmissionConflict) as exc_info:
        submit_result(submission)

    response = cast(Response, exception_handler(exc_info.value, {}))
    assert response.status_code == 409
    assert response.data["detail"] == "Unable to log result: Bot finished-bot is not currently in this match!"
