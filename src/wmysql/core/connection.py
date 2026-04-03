import pymysql
from pymysql.cursors import DictCursor, SSCursor
from typing import Optional, Any, Dict, List, Tuple, Union
import asyncio
from contextlib import contextmanager

from wmysql.exceptions import ConnectionError as WMysqlConnectionError


class ConnectionManager:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        charset: str = "utf8mb4",
        connect_timeout: int = 10,
        autocommit: bool = False,
    ):
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": charset,
            "connect_timeout": connect_timeout,
            "autocommit": autocommit,
        }
        self._connection: Optional[pymysql.Connection] = None

    def connect(self) -> pymysql.Connection:
        try:
            self._connection = pymysql.connect(**self.config)
            return self._connection
        except pymysql.Error as e:
            raise WMysqlConnectionError(f"Failed to connect to MySQL: {e}")

    def get_connection(self) -> pymysql.Connection:
        if self._connection is None or not self._connection.open:
            return self.connect()
        return self._connection

    def close(self) -> None:
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        return self.get_connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        self.close()

    def commit(self) -> None:
        if self._connection and self._connection.open:
            self._connection.commit()

    def rollback(self) -> None:
        if self._connection and self._connection.open:
            self._connection.rollback()

    def execute(
        self, query: str, params: Optional[Tuple] = None
    ) -> pymysql.cursors.Cursor:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor

    def execute_many(self, query: str, params: Optional[List[Tuple]] = None) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params)

    def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        cursor = self.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict]:
        cursor = self.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result


class AsyncConnectionManager:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "",
        charset: str = "utf8mb4",
        connect_timeout: int = 10,
        autocommit: bool = False,
    ):
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": charset,
            "connect_timeout": connect_timeout,
            "autocommit": autocommit,
        }
        self._connection: Optional[pymysql.connections.Connection] = None

    async def connect(self) -> pymysql.connections.Connection:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._connection = await pymysql.connect(
            **self.config,
            loop=loop,
        )
        return self._connection

    async def get_connection(self) -> pymysql.connections.Connection:
        if self._connection is None or not self._connection.open:
            return await self.connect()
        return self._connection

    async def close(self) -> None:
        if self._connection and self._connection.open:
            self._connection.close()
            self._connection = None

    async def commit(self) -> None:
        if self._connection and self._connection.open:
            self._connection.commit()

    async def rollback(self) -> None:
        if self._connection and self._connection.open:
            self._connection.rollback()

    async def execute(
        self, query: str, params: Optional[Tuple] = None
    ) -> pymysql.cursors.Cursor:
        conn = await self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor

    async def fetch_all(self, query: str, params: Optional[Tuple] = None) -> List[Dict]:
        cursor = await self.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    async def fetch_one(
        self, query: str, params: Optional[Tuple] = None
    ) -> Optional[Dict]:
        cursor = await self.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result


class Transaction:
    def __init__(self, connection_manager: ConnectionManager):
        self._cm = connection_manager
        self._conn: Optional[pymysql.Connection] = None
        self._cursor: Optional[pymysql.cursors.Cursor] = None
        self._committed = False
        self._rolled_back = False

    def __enter__(self):
        self._conn = self._cm.get_connection()
        self._conn.begin()
        self._cursor = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        elif not self._committed and not self._rolled_back:
            self._conn.rollback()
        if self._cursor:
            self._cursor.close()
        self._conn = None
        self._cursor = None

    def execute(
        self, query: str, params: Optional[Tuple] = None
    ) -> pymysql.cursors.Cursor:
        if self._cursor is None:
            raise RuntimeError("Transaction not started")
        self._cursor.execute(query, params)
        return self._cursor

    def commit(self) -> None:
        if self._conn:
            self._conn.commit()
            self._committed = True

    def rollback(self) -> None:
        if self._conn:
            self._conn.rollback()
            self._rolled_back = True


class AsyncTransaction:
    def __init__(self, connection_manager: AsyncConnectionManager):
        self._cm = connection_manager
        self._conn: Optional[pymysql.connections.Connection] = None
        self._cursor: Optional[pymysql.cursors.Cursor] = None
        self._committed = False
        self._rolled_back = False

    async def __aenter__(self):
        self._conn = await self._cm.get_connection()
        self._conn.begin()
        self._cursor = self._conn.cursor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        elif not self._committed and not self._rolled_back:
            await self.rollback()
        if self._cursor:
            self._cursor.close()
        self._conn = None
        self._cursor = None

    async def execute(
        self, query: str, params: Optional[Tuple] = None
    ) -> pymysql.cursors.Cursor:
        if self._cursor is None:
            raise RuntimeError("Transaction not started")
        self._cursor.execute(query, params)
        return self._cursor

    async def commit(self) -> None:
        if self._conn:
            self._conn.commit()
            self._committed = True

    async def rollback(self) -> None:
        if self._conn:
            self._conn.rollback()
            self._rolled_back = True


__all__ = [
    "ConnectionManager",
    "AsyncConnectionManager",
    "Transaction",
    "AsyncTransaction",
]
