from typing import Callable, TypeVar
from enum import Enum

from discord.app_commands import Cooldown

# noinspection PyProtectedMember
from discord.app_commands.checks import _create_cooldown_decorator

T = TypeVar('T')


class Btypes(Enum):
    guild = lambda i: (i.guild_id, i.guild_id)
    channel = lambda i: (i.guild_id, i.channel_id)
    user = lambda i: (i.guild_id, i.user.id)


def koeldown(rate: float | int, per: float | int, btype: Btypes) -> Callable[[T], T]:
    return _create_cooldown_decorator(btype, lambda interaction: Cooldown(rate, per))
