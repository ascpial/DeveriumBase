from __future__ import annotations
from typing import TYPE_CHECKING

import importlib
import inspect
import pkgutil
from typing import Generator, NoReturn, Tuple

from nextcord.ext.commands import Context

if TYPE_CHECKING:
    from .config import Configuration

def unqualify(name: str) -> str:
    """Return an unqualified name given a qualified module/package `name`."""
    return name.rsplit(".", maxsplit=1)[-1]


def walk_extensions(config: Configuration):
    """Yield extension names from extensions sub package."""

    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)  # pragma: no cover

    for module in pkgutil.walk_packages(
        (config.extensions_path,),
        f"{config.extensions_path}.",
        onerror=on_error
    ):
        if unqualify(module.name).startswith("_"):
            # Ignore module/package names starting with an underscore.
            continue

        imported = importlib.import_module(module.name)
        if not inspect.isfunction(getattr(imported, "setup", None)):
            # If it lacks a setup function, it's not an extension.
            continue
        
        yield module.name
