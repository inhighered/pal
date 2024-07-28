import os
from functools import wraps
from typing import Tuple
from dataclasses import fields

import psycopg
from psycopg import Connection

from logging import getLogger
_logger = getLogger(__name__)


def get_db_params():
    conn_parameters = {
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'host': os.getenv("DB_HOST"),
        'dbname': os.getenv("DB_NAME"),
        'autocommit': True
    }

    return conn_parameters


def with_connection(func):
    def wrapper(*args, **kwargs):
        params = get_db_params()
        conn = psycopg.connect(**params)

        try:
            response = func(conn, *args, **kwargs)
        except Exception as e:
            conn.rollback()
            _logger.error(f"Error in {func.__name__} - {e}")
            raise e
        
        else:
            conn.commit()
        finally:
            conn.close()
        
        return response
    
    return wrapper



def cache_query(func):

    memo = {}
    @wraps(func)
    def wrapper(*args, **kwargs):

        # don't cache connection object
        is_connector = False
        hashable_args = []
        for arg in args:
            if type(arg) == Connection:
                is_connector = True
            else:
                hashable_args.append(arg)

        if not is_connector:
            raise ValueError("Connection object not found in args")
        
        hashable_args = tuple(hashable_args) + tuple(kwargs.items())

        if hashable_args in memo:
            _logger.debug(
                f"Using cached content for: \n {str(hashable_args)} and {str(func)}"
                )
            return memo[hashable_args]
        
        else:
            _logger.debug(
                f"No cached content for: {str(hashable_args)} and {str(func)}"
            )
            results = func(*args, **kwargs)
            memo[hashable_args] = results
            return results
        
    def clear_cache() -> None:
        memo.clear()
        _logger.debug("Query cache cleared")
        return None
    
    wrapper.clear_cache = clear_cache

    return wrapper


@cache_query
@with_connection
def query(conn: Connection, sql:str) -> Tuple[tuple, tuple]:
    _logger.debug(f"Executing query: {sql}")

    cursor = conn.cursor()
    cursor.execute(sql)
    col_names = cursor.description
    rows = cursor.fetchall()
    cursor.close()

    return col_names, rows


@with_connection
def query_no_cache(conn: Connection, sql:str) -> Tuple[tuple, tuple]:
    _logger.debug(f"Executing query: {sql}")

    cursor = conn.cursor()
    cursor.execute(sql)
    col_names = cursor.description
    rows = cursor.fetchall()
    cursor.close()

    return col_names, rows


@with_connection
def insert_with_conn(conn: Connection, sql:str, values: Tuple) -> None:
    _logger.debug(f"Executing query: {sql} with values {values}")

    cursor = conn.cursor()
    cursor.execute(sql, values)
    cursor.close()
    conn.commit()


def validate_types(typed_class):
    for field in fields(typed_class):
        value = getattr(typed_class, field.name)
        if not isinstance(value, field.type):
            raise ValueError(f"Field {field.name} is not of type {field.type} - type is {type(value)}")