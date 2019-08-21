# pip-install.py
# This script will run pip install for the ENVIRONMENT_TYPE configured in ./aiarena/settings

import os
import sys
from subprocess import run

from aiarena.settings import ENVIRONMENT_TYPE

_LOCAL_DIRECTORY = os.path.dirname(__file__)
_STANDARD_REQUIREMENTS_FILE = os.path.join(_LOCAL_DIRECTORY, "requirements.txt")
_ENVIRONMENT_REQUIREMENTS_FILE = os.path.join(_LOCAL_DIRECTORY, f"requirements.{ENVIRONMENT_TYPE.name}.txt")
_DEFAULT_PIP_BINARY = "pip3"

# Require Python 3.7
_PYTHON_REQUIRED_VERSION_MAJOR = 3
_PYTHON_REQUIRED_VERSION_MINOR = 7


def print_usage():
    print("Usage: python pip-install.py [pip_binary]" + os.linesep
          + "\tpip_binary: The path to or name of the PIP binary to use. Default: pip3")


def verify_python_version():
    if sys.version_info[0] != _PYTHON_REQUIRED_VERSION_MAJOR or sys.version_info[1] != _PYTHON_REQUIRED_VERSION_MINOR:
        raise Exception("This install procedure requires Python {0}.{1}".format(_PYTHON_REQUIRED_VERSION_MAJOR,
                                                                                _PYTHON_REQUIRED_VERSION_MINOR))


def run_install(pip_binary_name):
    # requirements - standard across all environments
    run(pip_binary_name + " install -r " + _STANDARD_REQUIREMENTS_FILE + " --no-input", shell=True, check=True)

    # environment type specific requirements
    run(pip_binary_name + " install -r " + _ENVIRONMENT_REQUIREMENTS_FILE + " --no-input", shell=True, check=True)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_install(_DEFAULT_PIP_BINARY)
    elif sys.argv[1] != '--help':
        run_install(sys.argv[1])
    else:
        print_usage()
