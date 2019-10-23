# pip-install.py
# This script will run pip install for the ENVIRONMENT_TYPE configured in ./aiarena/settings

import optparse
import os
import sys
from subprocess import run

# Add the parent dir to the PYTHONPATH so we can more easily import aiarena.settings
# Is this a good idea?
sys.path.append(sys.path[0] + "/..")
from aiarena.settings import ENVIRONMENT_TYPE

_LOCAL_DIRECTORY = os.path.dirname(__file__)
_STANDARD_REQUIREMENTS_FILE = os.path.join(_LOCAL_DIRECTORY, "requirements.txt")
_ENVIRONMENT_REQUIREMENTS_FILE = os.path.join(_LOCAL_DIRECTORY, f"requirements.{ENVIRONMENT_TYPE.name}.txt")
_PROJECT_ROOT_DIRECTORY = os.path.join(_LOCAL_DIRECTORY, "..")
_DEFAULT_PIP_BINARY = "pip3"
_DEFAULT_PYTHON_BINARY = "python3"

# Require Python 3.7
_PYTHON_REQUIRED_VERSION_MAJOR = 3
_PYTHON_REQUIRED_VERSION_MINOR = 7


def verify_python_version():
    if sys.version_info[0] != _PYTHON_REQUIRED_VERSION_MAJOR or sys.version_info[1] != _PYTHON_REQUIRED_VERSION_MINOR:
        raise Exception("This install procedure requires Python {0}.{1}".format(_PYTHON_REQUIRED_VERSION_MAJOR,
                                                                                _PYTHON_REQUIRED_VERSION_MINOR))


def run_install(pip_binary_name, python_binary_name):
    print('RUNNING INSTALL PROCEDURE')
    # requirements - standard across all environments
    run(pip_binary_name + " install -r " + _STANDARD_REQUIREMENTS_FILE + " --no-input", shell=True, check=True)

    # environment type specific requirements
    run(pip_binary_name + " install -r " + _ENVIRONMENT_REQUIREMENTS_FILE + " --no-input", shell=True, check=True)

    # Run django-discord-bind setup
    run(python_binary_name + " " + os.path.join(_PROJECT_ROOT_DIRECTORY, "django-discord-bind/setup.py")
        + " install --force", shell=True, check=True)
    print('INSTALL PROCEDURE COMPLETE')


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.set_defaults(pip=_DEFAULT_PIP_BINARY, python=_DEFAULT_PYTHON_BINARY)
    parser.add_option('--pip', dest='pip')
    parser.add_option('--python', dest='python')
    (options, args) = parser.parse_args()

    run_install(options.pip, options.python)
