"""Per-match command line arguments passed on to the bot processes.

A requested match can carry one free-form ASCII string per bot, supplied by the
requester. It lets the requester give a bot context that isn't part of its zip —
"you are playing in a tournament", "play your cheese build" — without the bot
author having to time an upload around it. Ladder matches never carry any.

The string is the bot's extra command line, and it travels **verbatim**:
website, database, API, arena client, bot process. Nothing along the way
rewrites it. The arena client splits it into arguments the way a shell would,
at the moment it builds the command — so a quoted space stays inside one
argument, and ``--message="good luck"`` reaches the bot as a single argument.

That makes this module the only place that inspects the contents, and it does so
without changing them: it parses to find out whether the string is usable and
then throws the result away. Everything here is a check, never a conversion.

The arena client's own splitting has to agree with the splitting done here, or a
string accepted at submit time could reach a bot as something else. That is what
the shared table of cases in the tests is for, in this repo and in the arena
client's.
"""

import shlex


MAX_LENGTH = 500
"""Upper bound on one bot's string. Generous for a handful of flags, small
enough that the arguments stay reviewable in a match listing."""

RESERVED_FLAGS = frozenset(
    {
        "gameport",
        "ladderserver",
        "startport",
        "opponentid",
    }
)
"""Arguments the arena client passes to every bot itself.

A requester must not be able to set these. They decide which game the bot joins
and who it thinks it is playing, so overriding one on someone else's bot is a
way to break their match or point them at a server of your choosing — and the
arguments here land on the *opponent's* command line as readily as your own.

Kept as a denylist because the strings now reach the bot untouched, so there is
no namespace left to confine them to. It has to be updated alongside the
arguments the arena client passes; the names live in bot_controller there.
"""


def split_bot_args(raw: str | None) -> list[str]:
    """Split one bot's args string into words, shell-style.

    Raises ValueError if the quoting doesn't close. Callers use this to find out
    whether a string is usable, never to store or serve the result — the string
    itself is what travels.
    """
    return shlex.split(raw or "")


def reserved_flags_in(raw: str | None) -> list[str]:
    """The reserved flag names this string would hand to a bot, in order.

    Matches the spelling a bot's argument parser would see, so ``--LadderServer``
    and ``--LadderServer=host`` are both found, in any case.
    """
    found = []
    for word in split_bot_args(raw):
        name = word.split("=", 1)[0].lstrip("-")
        if name.lower() in RESERVED_FLAGS:
            found.append(name)
    return found
