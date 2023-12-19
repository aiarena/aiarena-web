import os
from enum import Enum


class ENVIRONMENT_TYPES(Enum):
    DEVELOPMENT = 1
    PRODUCTION = 2


env = os.getenv("DJANGO_ENVIRONMENT")
if env is None:
    print("DJANGO_ENVIRONMENT not set. Defaulting to DEVELOPMENT")
    env = "DEVELOPMENT"

ENVIRONMENT_TYPE = ENVIRONMENT_TYPES[env]
if ENVIRONMENT_TYPE == ENVIRONMENT_TYPES.PRODUCTION:
    from .prod import *  # noqa: F403, F405
elif ENVIRONMENT_TYPE == ENVIRONMENT_TYPES.DEVELOPMENT:
    try:
        from .local import *  # noqa: F403, F405
    except ImportError as e:
        if e.name != "aiarena.settings.local":
            raise
        from .dev import *  # noqa: F403, F405
else:
    raise Exception(f"Unrecognized DJANGO_ENVIRONMENT set: {ENVIRONMENT_TYPE}")
