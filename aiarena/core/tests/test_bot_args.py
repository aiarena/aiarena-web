from django.core.exceptions import ValidationError

import pytest

from aiarena.core.bot_args import reserved_flags_in, split_bot_args
from aiarena.core.validators import validate_bot_args


# The cases here are the contract the arena client's own splitting has to match.
# Keep them in step with the equivalent table in sc2-ai-match-controller.
@pytest.mark.parametrize(
    "raw,expected",
    [
        ("", []),
        (None, []),
        ("   ", []),
        ("--tournament=worldcup", ["--tournament=worldcup"]),
        ("--a --b --c", ["--a", "--b", "--c"]),
        ("--a\t--b\n  --c", ["--a", "--b", "--c"]),
        # Quotes group and then disappear, as in a shell.
        ('--score="1:3"', ["--score=1:3"]),
        ("--score='1:3'", ["--score=1:3"]),
        ('--message="good luck"', ["--message=good luck"]),
        ('"--message=good luck" --x', ["--message=good luck", "--x"]),
        ("--message=good\\ luck", ["--message=good luck"]),
        # A flag and its value as separate words stay separate.
        ("--build all in", ["--build", "all", "in"]),
    ],
)
def test_split_bot_args(raw, expected):
    assert split_bot_args(raw) == expected


@pytest.mark.parametrize("raw", ['--message="unclosed', "--message='unclosed", "--trailing\\"])
def test_split_bot_args_rejects_unclosed_quoting(raw):
    with pytest.raises(ValueError):
        split_bot_args(raw)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("--tournament=worldcup", []),
        # Every spelling a bot's argument parser would accept.
        ("--LadderServer=evil.host", ["LadderServer"]),
        ("--LadderServer evil.host", ["LadderServer"]),
        ("--ladderserver=evil.host", ["ladderserver"]),
        ("--LADDERSERVER=evil.host", ["LADDERSERVER"]),
        ("-LadderServer=evil.host", ["LadderServer"]),
        ('--LadderServer="evil.host"', ["LadderServer"]),
        ("--GamePort=9999", ["GamePort"]),
        ("--StartPort=9999", ["StartPort"]),
        ("--OpponentId=spoofed", ["OpponentId"]),
        ("--ok --GamePort=1 --OpponentId=2", ["GamePort", "OpponentId"]),
        # Not reserved: a longer name that merely starts with one.
        ("--GamePorts=9999", []),
    ],
)
def test_reserved_flags_in(raw, expected):
    assert reserved_flags_in(raw) == expected


def test_validate_bot_args_rejects_reserved_flags():
    """A requester must not be able to redirect a bot - theirs or the
    opponent's - to a game or server of their choosing."""
    with pytest.raises(ValidationError, match="cannot be overridden"):
        validate_bot_args("--LadderServer=evil.host")


def test_validate_bot_args_rejects_non_ascii():
    with pytest.raises(ValidationError, match="printable ASCII"):
        validate_bot_args("--build=cheesé")


def test_validate_bot_args_rejects_unclosed_quote():
    with pytest.raises(ValidationError, match="No closing quotation"):
        validate_bot_args('--message="oops')


def test_validate_bot_args_returns_the_string_unchanged():
    """The value that reaches the bot is the one submitted - validation looks
    but never rewrites."""
    raw = '--tournament=worldcup --message="good luck"'
    assert validate_bot_args(raw) == raw
