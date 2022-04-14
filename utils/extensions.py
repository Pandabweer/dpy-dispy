import importlib
import inspect
import pkgutil

from typing import Iterator, NoReturn

import ext
from discord.app_commands import Group


def unqualify(name: str) -> str:
    """Return an unqualified name given a qualified module/package `name`."""
    return name.rsplit(".", maxsplit=1)[-1]


def walk_extensions() -> Iterator[str]:
    """Yield extension names from the bot.exts subpackage."""

    def on_error(err_name: str) -> NoReturn:
        raise ImportError(name=err_name)  # pragma: no cover

    for module in pkgutil.walk_packages(ext.__path__, f"{ext.__name__}.", onerror=on_error):
        if unqualify(module.name).startswith("_"):
            # Ignore module/package names starting with an underscore.
            continue

        if module.ispkg:
            imported = importlib.import_module(module.name)
            for name, obj in inspect.getmembers(imported):
                if inspect.isclass(obj) and issubclass(obj, Group):
                    # https://github.com/Rapptz/discord.py/blob/master/discord/ext/commands/bot.py#L899
                    # obj.__name__
                    yield obj


EXTENSIONS = frozenset(walk_extensions())
