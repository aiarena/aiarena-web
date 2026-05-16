"""Centralized boto3 session management.

In CI/CD (GitHub Actions OIDC) the credentials are ambient via
AWS_ACCESS_KEY_ID; locally we fall back to the AWS_PROFILE matching the
project name, the same convention used by the legacy `aws cli` wrapper.
"""

import os

import boto3

from .settings import AWS_REGION, PROJECT_NAME


def get_boto3_session(region: str | None = None) -> boto3.Session:
    if region is None:
        region = AWS_REGION

    if os.environ.get("AWS_ACCESS_KEY_ID"):
        return boto3.Session(region_name=region)

    profile = os.environ.get("AWS_PROFILE") or PROJECT_NAME
    return boto3.Session(profile_name=profile, region_name=region)
