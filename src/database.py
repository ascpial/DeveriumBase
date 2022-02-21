from __future__ import annotations
from typing import Any, Optional, TypeVar

import logging
import pathlib

import sqlite3

from .utils import MISSING

__all__ = (
    'python_type_to_sql_type',
    'DatabaseColumn',
    'DatabaseTable',
    'DatabaseConfig',
    'Database',
)

T = TypeVar('T')

def python_type_to_sql_type(type: type) -> str:
    if type is str:
        return 'TEXT'
    elif type is int:
        return 'INTEGER'
    elif type is float:
        return 'REAL'

def adapt(value: str | int | float) -> str:
    # this is only for the extension developer.
    # this method should not be used to store user data
    if isinstance(value, str):
        if '\"' not in value:
            return f'\"{value}\"'
        else:
            if '\'' not in value:
                return f'\'{value}\''
            value = value.replace('\'', '\'\'')
            return f"'{value}'"
    elif isinstance(value, int | float):
        return str(value)

class DatabaseColumn:
    def __init__(
        self,
        name: str,
        type: T = str,
        not_null: bool = False,
        default: T = MISSING,
        primary_key: bool = False,
    ):
        self.name = name
        self.type = type
        self.not_null = not_null
        self.default = default
        self.primary_key = primary_key
    
    def get_create_column(self) -> str:
        sql_type = python_type_to_sql_type(self.type)
        partial_query = f"{self.name} {sql_type}"
        
        if self.primary_key:
            partial_query += ' PRIMARY KEY'
        if self.not_null:
            partial_query += ' NOT NULL'
        if self.default is not MISSING:
            partial_query += ' DEFAULT {}'.format(
                adapt(self.default)
            )
        
        return partial_query

class DatabaseTable:
    def __init__(
        self,
        name: str,
        columns: list[DatabaseColumn],
    ):
        self.name = name
        self.columns = {
            column.name: column for column in columns
        }
    
    def get_create_statement(
        self,
        if_not_exists: bool = True,
    ) -> str:
        query = f"CREATE TABLE {'IF NOT EXISTS ' if if_not_exists else ''}{self.name} (\n    "
        columns: list[str] = []
        for column in self.columns.values():
            partial_query = column.get_create_column()
            columns.append(partial_query)
        query += ',\n    '.join(
            (columns)
        )
        query += '\n);'
        
        return query

class DatabaseConfig:
    tables: dict[str, DatabaseTable]
    
    def __init__(
        self,
    ):
        self.tables = {}
    
    def add_table(self, table: DatabaseTable):
        if table.name in self.tables:
            raise ValueError(
                f'a table with the name {repr(table.name)} already exists in the database config'
            )
        self.tables[table.name] = table
    
    def remove_table(self, table: DatabaseTable):
        if table.name not in self.tables:
            raise ValueError(
                f'the table {repr(table.name)} is not in the database config'
            )
        del self.tables[table.name]


class Database:
    tables: dict[str, DatabaseTable]
    configurations: list[DatabaseConfig]
    
    def __init__(
        self,
        database_path: str | pathlib.Path,
    ):
        self.database_path = database_path
        
        self.connection = None
        self.tables = {}
        self.configurations = []
        
        self.connect()
        
    def connect(self) -> sqlite3.Connection:
        # close the connection if applicable
        if self.connection is not None:
            self.connection.close()
        
        # create the connection
        self.connection: sqlite3.Connection = sqlite3.connect(
            self.database_path,
        )
        return self.connection

    def update_tables(self, overwrite=False):
        """Create the missing tables contained in the database configuration.
        
        The existing tables that are not present in the configuration are not
        deleted.
        
        Parameters
        ----------
        overwrite: bool = False
            If overwrite is ``True``, the old tables are deleted and the new
            ones are created after that. ``overwrite = True`` remove all
            previous data present in the database for the specified tables.
        """
        cursor = self.connection.cursor()
        
        for table in self.tables.values():
            if overwrite: # if we overwrite, we drop the table first
                cursor.execute(f'DROP TABLE IF EXISTS {table.name}')

            # the table should not exists if overwrite but we remove the
            # IF NOT EXISTS clause anyway
            query = table.get_create_statement(if_not_exists=not overwrite)
            
            cursor.execute(query)
        
        cursor.close()
        
        self.connection.commit()
    
    def add_configuration(self, configuration: DatabaseConfig):
        if configuration in self.configurations:
            raise ValueError(
                f'the configuration {repr(configuration)} is already in the database',
            )
        
        for table in configuration.tables.values():
            if table.name not in self.tables:
                self.tables[table.name] = table
            else:
                raise ValueError(f'a table with the name {repr(table.name)} if already in the database')
        
        self.configurations.append(configuration)
    
    def remove_configuration(self, configuration: DatabaseConfig):
        try:
            self.configurations.remove(DatabaseConfig)
        except ValueError:
            raise ValueError(f'the configuration {repr(configuration)} is not in the database')
        else:
            for table in configuration:
                try:
                    self.remove_table(table)
                except ValueError:
                    logging.warn(
                        f'ignoring exception when removing configuration {repr(configuration)}:'
                        f'the table {repr(table)} is not present in the database'
                    )
    
    def add_table(self, table: DatabaseTable):
        if table.name in self.tables:
            raise ValueError(
                f'a table with the name {repr(table.name)} already exists in the database'
            )
        self.tables[table.name] = table
    
    def remove_table(self, table: DatabaseTable):
        if table.name not in self.tables:
            raise ValueError(
                f'the table {repr(table.name)} is not in the database config'
            )
        del self.tables[table.name]