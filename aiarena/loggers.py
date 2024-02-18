import json
import time
from functools import cached_property
from pprint import pprint

from django.conf import settings

import boto3
import sentry_sdk

from aiarena.core.utils import ReprJSONEncoder


class AbstractLogger:
    def send(self, payload: dict):
        raise NotImplementedError


class CloudWatchLogger(AbstractLogger):
    @cached_property
    def client(self):
        return boto3.client("logs")

    def ensure_log_group_and_stream_exist(self, log_group, log_stream):
        try:
            self.client.create_log_group(logGroupName=log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

        try:
            self.client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

    def send(self, payload: dict, log_group="default", log_stream="default"):
        from aiarena.core.tasks import task_info_context

        payload |= task_info_context()
        try:
            message = json.dumps(payload, cls=ReprJSONEncoder)
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
            return

        log_args = {
            "logGroupName": log_group,
            "logStreamName": log_stream,
            "logEvents": [{"timestamp": int(round(time.time() * 1000)), "message": message}],
        }

        try:
            self.client.put_log_events(**log_args)
        except self.client.exceptions.ResourceNotFoundException:
            self.ensure_log_group_and_stream_exist(log_group, log_stream)
            self.client.put_log_events(**log_args)


class ConsoleLogger(AbstractLogger):
    def send(self, payload: dict):
        from aiarena.core.tasks import task_info_context

        pprint(payload | task_info_context())  # noqa: T203


class DummyLogger(AbstractLogger):
    def send(self, payload: dict):
        pass


if settings.RUNNING_TESTS:
    logger = DummyLogger()
elif settings.DEBUG:
    logger = ConsoleLogger()
else:
    logger = CloudWatchLogger()
