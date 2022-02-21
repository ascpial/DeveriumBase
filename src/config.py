from __future__ import annotations
import pathlib
from typing import Any, Optional

import os
import json

from .utils import MISSING

__all__ = (
    'ConfigurationData',
    'Configuration',
)

# default configuration states
DEFAULT_EXTENSIONS_PATH = 'extensions'
DEFAULT_PREFIX = ['!']
DEFAULT_DATABASE_PATH = 'data/database.db'

class ConfigurationData:
    """This class represent the raw data from a payload.
    
    Parameters
    ----------
    data: Dict[str, Any]
        The raw data used to initialize the configuration
    
    name: Optional[str]
        The name of the configuration instance.
        If None, the configuration is the root configuration.
    
    Attributes
    ----------
    token: str
        The token of the bot
    extensions_path: str
        The name of the extension sub package
    """
    token: str
    extensions_path: str
    prefix: list[str]
    
    def __init__(self, data: dict[str, Any], name: str = None):
        self.name = name
        self.token = data.get('token', MISSING)
        self.extensions_path = data.get('extensions_path', MISSING)
        self.prefix = data.get('prefix', MISSING)
        self.database_path = data.get('database', MISSING)
    
    def get_field(self, name: str) -> Any:
        """Returns the configuration value corresponding to ``name``.
        
        Parameters
        ----------
        name: str
            The name of the configuration field
        
        Returns
        -------
        Any
            The value of the configuration field
        """
        return getattr(self, name)

class Configuration:
    instance: Optional[ConfigurationData]
    
    def __init__(
        self,
        file: Optional[str | os.PathLike] = None,
        instance: str = None
    ):
        self.instance_name = instance
        
        # reading the config file
        if file is not None:
            with open(file, encoding='utf-8') as config_file:
                raw_config: dict[str, Any] = json.load(config_file)
        else:
            raw_config = {} # empty config
        
        # load the default root configuration
        self.default_configuration = ConfigurationData(raw_config)
        
        # load each instance configuration
        self.instances: dict[ConfigurationData] = {}
        for name, raw_instance in raw_config.get('instances', {}).items():
            self.instances[name] = ConfigurationData(raw_instance)
        
        # load the selected instance if any
        if self.instance_name is not None:
            if self.instance_name in self.instances:
                self.instance = self.instances[self.instance_name]
            else:
                raise ValueError('the specified instance does not exists in the configuration file')
        else:
            self.instance = None
    
    def get_field(self, name: str) -> Any:
        """Return the configuration field corresponding to the specified name.
        
        This function first check if the field is present in the selected
        instance if applicable and then return the default configuration
        field value.
        
        Parameters
        ----------
        name: str
            The configuration field name
        
        Returns
        -------
        Any
            The data corresponding to the field.
            Could be ``None`` and ``MISSING``.
        """
        # first we check if the field is in the selected instance
        if self.instance is not None:
            if self.instance.get_field(name) is not MISSING:
                return self.instance.get_field(name)
        
        # if it is not case we return the default value
        return self.default_configuration.get_field(name)

    @property
    def token(self) -> str:
        """The token of the bot"""
        return self.get_field('token')

    @property
    def extensions_path(self) -> str:
        """The extension sub package name"""
        configured_path = self.get_field('extensions_path')
        if configured_path is MISSING:
            return DEFAULT_EXTENSIONS_PATH
        else:
            return configured_path
    
    @property
    def prefix(self) -> str:
        """The list of default prefix of the bot"""
        configured_prefix = self.get_field('prefix')
        if configured_prefix is MISSING:
            return DEFAULT_PREFIX
        else:
            return configured_prefix
    
    @property
    def database_path(self) -> str | pathlib.Path:
        """The database location"""
        configured_database = self.get_field('database_path')
        if configured_database is MISSING:
            return DEFAULT_DATABASE_PATH
        else:
            return configured_database