import os

from ..core.utils import EnvironmentType


env = os.getenv("DJANGO_ENVIRONMENT")
if env is None:
    raise Exception("The environment variable DJANGO_ENVIRONMENT must be set to one of: DEVELOPMENT, PRODUCTION")

ENVIRONMENT_TYPE = EnvironmentType[env]
if ENVIRONMENT_TYPE == EnvironmentType.PRODUCTION:
    from .prod import *  # noqa: F403, F405
elif ENVIRONMENT_TYPE == EnvironmentType.DEVELOPMENT:
    try:
        from .local import *  # noqa: F403, F405
    except ImportError as e:
        if e.name != "aiarena.settings.local":
            raise
        from .dev import *  # noqa: F403, F405
else:
    raise Exception(f"Unrecognized DJANGO_ENVIRONMENT set: {ENVIRONMENT_TYPE}")
