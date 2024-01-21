import logging
import psycopg
from psycopg import abc as psy_abc

from psycopg import rows
import psycopg_pool

import config

from typing import Optional, TypeVar, Generic, Type

logger = logging.getLogger(__name__)

_pool_default = None


def get_pool():
    global _pool_default
    if _pool_default:
        return _pool_default
    _pool_default = psycopg_pool.ConnectionPool(
        min_size=config.POOL_MIN_SIZE,
        max_size=config.POOL_MAX_SIZE,
        max_idle=config.POOL_MAX_IDLE,
    )
    return _pool_default


class RowFactoryError(Exception):
    pass


T = TypeVar("T")


def row_factory(cls: Type[T]):
    def _row_factory(cursor: psycopg.Cursor[T]):
        description = cursor.description
        if not description:
            raise RowFactoryError("Invalid cursor: must have columns.")
        columns = [column.name for column in description]

        def make_row(values):
            row = dict(zip(columns, values))
            return cls(**row)

        return make_row

    return _row_factory


def make_fetchone(cls: Type[T]):
    factory: rows.RowFactory[T] = row_factory(cls)

    def fetch(query: psy_abc.Query, params: Optional[psy_abc.Params] = None):
        with get_pool().connection() as conn, conn.cursor(row_factory=factory) as cur:
            cur.execute(query, params)
            return cur.fetchone()

    return fetch


def make_fetchmany(cls: Type[T]):
    factory: rows.RowFactory[T] = row_factory(cls)

    def fetch(query: psy_abc.Query, max: int, params: Optional[psy_abc.Params] = None):
        with get_pool().connection() as conn, conn.cursor(row_factory=factory) as cur:
            cur.execute(query, params)
            return cur.fetchmany(max)

    return fetch


def make_fetchall(cls: Type[T]):
    factory: rows.RowFactory[T] = row_factory(cls)

    def fetch(query: psy_abc.Query, params: Optional[psy_abc.Params] = None):
        with get_pool().connection() as conn, conn.cursor(row_factory=factory) as cur:
            cur.execute(query, params)
            return cur.fetchall()

    return fetch


def make_execute(cls: Type[T]):
    factory: rows.RowFactory[T] = row_factory(cls)

    def fetch(query: psy_abc.Query, params: Optional[psy_abc.Params] = None):
        with get_pool().connection() as conn, conn.cursor(row_factory=factory) as cur:
            cur.execute(query, params)

    return fetch


class ManagedCursor(Generic[T]):
    def __init__(self, type_: Type[T]):
        self.model = type_
        self.row_factory: rows.RowFactory[T] = ManagedCursor._row_factory(type_)

    @staticmethod
    def _row_factory(klass):
        def fac_func(cursor: psycopg.Cursor[T]):
            description = cursor.description
            if not description:
                raise RowFactoryError("Invalid cursor: must have columns.")
            columns = [column.name for column in description]

            def make_row(values):
                row = dict(zip(columns, values))
                return klass(**row)

            return make_row

        return fac_func

    def fetchone(self, query: psy_abc.Query, params: Optional[psy_abc.Params] = None):
        with get_pool().connection() as conn, conn.cursor(
            row_factory=self.row_factory
        ) as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def fetchmany(
        self, query: psy_abc.Query, size: int, params: Optional[psy_abc.Params] = None
    ):
        with get_pool().connection() as conn, conn.cursor(
            row_factory=self.row_factory
        ) as cur:
            cur.execute(query, params)
            return cur.fetchmany(size)

    def fetchall(self, query: psy_abc.Query, params: Optional[psy_abc.Params] = None):
        with get_pool().connection() as conn, conn.cursor(
            row_factory=self.row_factory
        ) as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute(self, query: psy_abc.Query, params: Optional[psy_abc.Params] = None):
        with get_pool().connection() as conn, conn.cursor(
            row_factory=self.row_factory
        ) as cur:
            cur.execute(query, params)
