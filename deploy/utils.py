import contextlib
import json
import os
import time
from collections.abc import Iterable
from functools import wraps
from pathlib import Path

import sarge


# Type for specifying an optional list of filenames mask (e.g. ["*.py"]).
OptMask = Iterable[str] | None


def timing(func):
    """
    Decorator which prints function execution time.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        func_args = ", ".join(
            [str(a) for a in args] + [f"{k}={v}" for k, v in kwargs.items()],
        )
        print(
            "\n--- {}({}): {:0.3f} sec ---\n\n".format(  # noqa T201
                func.__name__,
                func_args,
                time.time() - start,
            )
        )
        return result

    return inner


def echo(message, prefix="->> "):
    """
    Use ->> prefix to visually identify output produced by our script.
    """
    print("{}{}".format(prefix or "", message))  # noqa T201


def run(
    cmd,
    raise_on_error=True,
    capture_stdout=False,
    capture_stderr=False,
    parse_json=False,
    print_cmd=False,
    **kwargs,
):
    """
    Wrapper around sarge.run which can raise errors and capture stdout.
    """
    if capture_stdout:
        kwargs["stdout"] = sarge.Capture()
    if capture_stderr:
        kwargs["stderr"] = sarge.Capture()
    if print_cmd:
        echo(cmd)
    result = sarge.run(cmd, **kwargs)
    code = result.returncode
    if code and raise_on_error:
        msg = f'Command failed, exit code {code} - "{cmd}"'
        if capture_stdout and (stdout := result.stdout.read().decode()):
            msg = f"{msg}\n{'-' * 40}\n{stdout}"
        if capture_stderr and (stderr := result.stderr.read().decode()):
            msg = f"{msg}\n{'-' * 40}\n{stderr}"
        raise RuntimeError(msg)
    result.json = None
    if result.stdout:
        output = result.stdout.read()
        try:
            decoded = output.decode()
        except UnicodeDecodeError:
            raise RuntimeError(f"Non unicode chars in output: {output}")
        result.stdout_lines = decoded.split("\n")
        if result.stdout_lines[-1] == "":
            result.stdout_lines = result.stdout_lines[:-1]
        if parse_json:
            result.json = json.loads("\n".join(result.stdout_lines))
    else:
        result.stdout_lines = []
    return result


def run_with_retry(cmd, count=20, sleep=1, **kwargs):
    echo(f"Trying: {cmd}")
    for i in range(1, count + 1):
        if i > 1:
            time.sleep(sleep)
        echo(f"Attempt #{i}")
        try:
            result = run(cmd, **kwargs)
            echo(f"Attempt #{i} was successful")
            return result
        except RuntimeError:
            if i == count:
                echo(f"All {count} attempts failed")
                raise


@contextlib.contextmanager
def cd(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)


def str_to_bool(s):
    return s.lower() in ("yes", "y", "true", "1")


def env_as_cli_args(env):
    return " ".join(f'-e {k}="{v}"' for k, v in env.items())


def git_changed_files(mask: OptMask = None, only_staged: bool = False, commit_range: str = "") -> set[str]:
    """
    Return set of filenames changed or staged in git repository.

    :param mask: Optional list of extensions by which to filter modified files.
    :param exists: Check found files exist.
    :param only_staged: Return only staged files.
    :param commit_range: Get changed filed for the specific commit range.
    """
    if commit_range:
        filenames = git_commit_range_files(commit_range, mask)
    else:
        filenames = git_diff_files(mask, staged=True)
        if not only_staged:
            filenames |= git_diff_files(mask)
    filenames = {filename for filename in filenames if Path(filename).is_file()}
    return filenames


def git_diff_files(mask: OptMask = None, staged: bool = False) -> set[str]:
    """
    Return set of changed filenames relative to the last commit.

    :param mask: Optional list of extensions by which to filter modified files.
    :param staged: Find staged files relative to HEAD instead of changes in
        current working tree.
    """
    files = " ".join(f'"{fm}"' for fm in mask) if mask else ""
    cmd = " ".join(
        (
            "git diff",
            "--cached" if staged else "",
            "--ignore-space-at-eol",
            "--name-only",
            files,
        )
    )
    return set(run(cmd, capture_stdout=True).stdout_lines)


def git_commit_range_files(commit_range, mask: OptMask = None) -> set[str]:
    """
    Return set of changed filenames for the commit range.
    """
    files = " ".join(f'"{fm}"' for fm in mask) if mask else ""
    cmd = " ".join(
        (
            "git diff",
            "--ignore-space-at-eol",
            "--name-only",
            commit_range,
            files,
        )
    )
    return set(run(cmd, capture_stdout=True).stdout_lines)


def django_setting(container_name, setting_name):
    from .settings import PROJECT_PATH

    code_dir = PROJECT_PATH / "code"
    code: str = f"from config import {setting_name}; import json; print(json.dumps({setting_name}));"
    return run(
        f"docker run --rm -v {code_dir}:/code -i {container_name} bash -c \"cd /code && python -c '{code}'\"",
        capture_stdout=True,
        parse_json=True,
    ).json


def running_on_mac():
    return run("uname", capture_stdout=True).stdout_lines[0] == "Darwin"
