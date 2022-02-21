from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING

import asyncio

import nextcord
from nextcord.ext import commands

from .utils import MISSING
from .extensions import walk_extensions

__all__ = (
    'DeveriumBot',
)

if TYPE_CHECKING:
    from .config import Configuration

class DeveriumBot(commands.Bot):
    def __init__(
        self,
        config: Configuration,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        **options: Any,
    ):
        self.config = config
        super().__init__(
            commands.when_mentioned_or(*self.config.prefix),
            loop=loop,
            **options
        )
        self.loaded: bool = False
    
    def load(self):
        # loading all extensions in the extensions sub package
        for extension_name in walk_extensions(self.config):
            self.load_extension(extension_name)
        
        self.loaded = True
    
    def run(self, *args: Any, **kwargs: Any) -> None:
        """This function run the bot.
        
        The token is grab from the configuration object used when the object
        has been instantiated.
        """
        # check if the bot was already loaded
        if not self.loaded:
            self.load()
        
        if self.config.token is MISSING:
            raise ValueError("the token has not been correctly set in the configuration file")

        super().run(
            self.config.token,
            *args,
            **kwargs,
        )