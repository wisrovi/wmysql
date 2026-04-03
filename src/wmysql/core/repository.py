from typing import Any, Dict, List, Optional, Tuple, Type
import asyncio
from wmysql.core.connection import (
    ConnectionManager,
    AsyncConnectionManager,
    Transaction,
    AsyncTransaction,
)
from wmysql.core.sync import TableSync, AsyncTableSync
from wmysql.builders.query_builder import QueryBuilder
from wmysql.exceptions import QueryError, ValidationError


class WMysql:
    def __init__(self, connection_manager: ConnectionManager):
        self._cm = connection_manager
        self._table_sync = TableSync(connection_manager)
        self._query_builder = QueryBuilder()

    @property
    def connection(self) -> ConnectionManager:
        return self._cm

    @property
    def table_sync(self) -> TableSync:
        return self._table_sync

    def table(self, table_name: str) -> "WMysql":
        self._current_table = table_name
        return self

    def create(
        self,
        table: str,
        data: Dict[str, Any],
        return_id: bool = False,
    ) -> Optional[int]:
        if not data:
            raise ValidationError("Data cannot be empty")

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self._cm.execute(query, tuple(values))
        self._cm.commit()

        if return_id:
            return cursor.lastrowid
        return None

    def create_many(
        self,
        table: str,
        data_list: List[Dict[str, Any]],
    ) -> int:
        if not data_list:
            raise ValidationError("Data list cannot be empty")

        columns = ", ".join(data_list[0].keys())
        placeholders_list = []
        values = []

        for data in data_list:
            placeholders_list.append("(" + ", ".join(["%s"] * len(data)) + ")")
            values.extend(data.values())

        placeholders = ", ".join(placeholders_list)
        query = f"INSERT INTO {table} ({columns}) VALUES {placeholders}"

        self._cm.execute(query, tuple(values))
        self._cm.commit()

        return len(data_list)

    def get(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
    ) -> Optional[Dict[str, Any]]:
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"

        params = []
        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            params = list(filters.values())

        if order_by:
            query += f" ORDER BY {order_by} {order_direction}"

        query += " LIMIT 1"

        return self._cm.fetch_one(query, tuple(params) if params else None)

    def get_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"

        params = []
        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            params = list(filters.values())

        if order_by:
            query += f" ORDER BY {order_by} {order_direction}"

        if limit:
            query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"

        return self._cm.fetch_all(query, tuple(params) if params else None)

    def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        if not data:
            raise ValidationError("Data cannot be empty")

        set_parts = [f"{k} = %s" for k in data.keys()]
        set_clause = ", ".join(set_parts)
        values = list(data.values())

        query = f"UPDATE {table} SET {set_clause}"

        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            values.extend(list(filters.values()))

        self._cm.execute(query, tuple(values))
        self._cm.commit()

        return self._cm._connection.affected_rows

    def delete(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        query = f"DELETE FROM {table}"

        params = []
        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            params = list(filters.values())

        self._cm.execute(query, tuple(params) if params else None)
        self._cm.commit()

        return self._cm._connection.affected_rows

    def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        query = f"SELECT COUNT(*) as count FROM {table}"

        params = []
        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            params = list(filters.values())

        result = self._cm.fetch_one(query, tuple(params) if params else None)
        return result.get("count", 0) if result else 0

    def paginate(
        self,
        table: str,
        page: int = 1,
        per_page: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
    ) -> Dict[str, Any]:
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10

        total = self.count(table, filters)
        offset = (page - 1) * per_page

        items = self.get_all(
            table=table,
            filters=filters,
            columns=columns,
            order_by=order_by,
            order_direction=order_direction,
            limit=per_page,
            offset=offset,
        )

        total_pages = (total + per_page - 1) // per_page

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
        }

    def raw_query(
        self, query: str, params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        return self._cm.fetch_all(query, params)

    def raw_query_one(
        self, query: str, params: Optional[Tuple] = None
    ) -> Optional[Dict[str, Any]]:
        return self._cm.fetch_one(query, params)

    def execute(self, query: str, params: Optional[Tuple] = None) -> Any:
        cursor = self._cm.execute(query, params)
        self._cm.commit()
        return cursor

    def transaction(self) -> Transaction:
        return Transaction(self._cm)

    def query(self) -> QueryBuilder:
        return QueryBuilder()

    def execute_builder(self, builder: QueryBuilder, query_type: str = "select") -> Any:
        if query_type == "select":
            query, params = builder.build_select()
            return self._cm.fetch_all(query, tuple(params) if params else None)
        elif query_type == "insert":
            query, params = builder.build_insert()
            self._cm.execute(query, tuple(params))
            self._cm.commit()
            return True
        elif query_type == "bulk_insert":
            query, params = builder.build_bulk_insert()
            self._cm.execute(query, tuple(params))
            self._cm.commit()
            return True
        elif query_type == "update":
            query, params = builder.build_update()
            self._cm.execute(query, tuple(params))
            self._cm.commit()
            return self._cm._connection.affected_rows
        elif query_type == "delete":
            query, params = builder.build_delete()
            self._cm.execute(query, tuple(params))
            self._cm.commit()
            return self._cm._connection.affected_rows
        elif query_type == "count":
            query, params = builder.build_count()
            result = self._cm.fetch_one(query, tuple(params) if params else None)
            return result.get("count", 0) if result else 0
        else:
            raise ValueError(f"Unknown query type: {query_type}")


class AsyncWMysql:
    def __init__(self, connection_manager: ConnectionManager):
        self._cm = connection_manager
        self._table_sync = AsyncTableSync(connection_manager)
        self._query_builder = QueryBuilder()

    @property
    def connection(self) -> ConnectionManager:
        return self._cm

    @property
    def table_sync(self) -> AsyncTableSync:
        return self._table_sync

    async def create(
        self,
        table: str,
        data: Dict[str, Any],
        return_id: bool = False,
    ) -> Optional[int]:
        if not data:
            raise ValidationError("Data cannot be empty")

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = await self._cm.execute(query, tuple(values))
        await self._cm.commit()

        if return_id:
            return cursor.lastrowid
        return None

    async def create_many(
        self,
        table: str,
        data_list: List[Dict[str, Any]],
    ) -> int:
        if not data_list:
            raise ValidationError("Data list cannot be empty")

        columns = ", ".join(data_list[0].keys())
        placeholders_list = []
        values = []

        for data in data_list:
            placeholders_list.append("(" + ", ".join(["%s"] * len(data)) + ")")
            values.extend(data.values())

        placeholders = ", ".join(placeholders_list)
        query = f"INSERT INTO {table} ({columns}) VALUES {placeholders}"

        await self._cm.execute(query, tuple(values))
        await self._cm.commit()

        return len(data_list)

    async def get(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
    ) -> Optional[Dict[str, Any]]:
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"

        params = []
        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            params = list(filters.values())

        if order_by:
            query += f" ORDER BY {order_by} {order_direction}"

        query += " LIMIT 1"

        return await self._cm.fetch_one(query, tuple(params) if params else None)

    async def get_all(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"

        params = []
        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            params = list(filters.values())

        if order_by:
            query += f" ORDER BY {order_by} {order_direction}"

        if limit:
            query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"

        return await self._cm.fetch_all(query, tuple(params) if params else None)

    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        if not data:
            raise ValidationError("Data cannot be empty")

        set_parts = [f"{k} = %s" for k in data.keys()]
        set_clause = ", ".join(set_parts)
        values = list(data.values())

        query = f"UPDATE {table} SET {set_clause}"

        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            values.extend(list(filters.values()))

        cursor = await self._cm.execute(query, tuple(values))
        await self._cm.commit()

        return cursor.affected_rows if cursor else 0

    async def delete(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        query = f"DELETE FROM {table}"

        params = []
        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            params = list(filters.values())

        cursor = await self._cm.execute(query, tuple(params) if params else None)
        await self._cm.commit()

        return cursor.affected_rows if cursor else 0

    async def count(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        query = f"SELECT COUNT(*) as count FROM {table}"

        params = []
        if filters:
            where_parts = [f"{k} = %s" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_parts)
            params = list(filters.values())

        result = await self._cm.fetch_one(query, tuple(params) if params else None)
        return result.get("count", 0) if result else 0

    async def paginate(
        self,
        table: str,
        page: int = 1,
        per_page: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "ASC",
    ) -> Dict[str, Any]:
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10

        total = await self.count(table, filters)
        offset = (page - 1) * per_page

        items = await self.get_all(
            table=table,
            filters=filters,
            columns=columns,
            order_by=order_by,
            order_direction=order_direction,
            limit=per_page,
            offset=offset,
        )

        total_pages = (total + per_page - 1) // per_page

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
        }

    async def raw_query(
        self, query: str, params: Optional[Tuple] = None
    ) -> List[Dict[str, Any]]:
        return await self._cm.fetch_all(query, params)

    async def raw_query_one(
        self, query: str, params: Optional[Tuple] = None
    ) -> Optional[Dict[str, Any]]:
        return await self._cm.fetch_one(query, params)

    async def execute(self, query: str, params: Optional[Tuple] = None) -> Any:
        cursor = await self._cm.execute(query, params)
        await self._cm.commit()
        return cursor

    async def transaction(self) -> AsyncTransaction:
        return AsyncTransaction(self._cm)

    def query(self) -> QueryBuilder:
        return QueryBuilder()

    async def execute_builder(
        self, builder: QueryBuilder, query_type: str = "select"
    ) -> Any:
        if query_type == "select":
            query, params = builder.build_select()
            return await self._cm.fetch_all(query, tuple(params) if params else None)
        elif query_type == "insert":
            query, params = builder.build_insert()
            await self._cm.execute(query, tuple(params))
            await self._cm.commit()
            return True
        elif query_type == "bulk_insert":
            query, params = builder.build_bulk_insert()
            await self._cm.execute(query, tuple(params))
            await self._cm.commit()
            return True
        elif query_type == "update":
            query, params = builder.build_update()
            cursor = await self._cm.execute(query, tuple(params))
            await self._cm.commit()
            return cursor.affected_rows if cursor else 0
        elif query_type == "delete":
            query, params = builder.build_delete()
            cursor = await self._cm.execute(query, tuple(params))
            await self._cm.commit()
            return cursor.affected_rows if cursor else 0
        elif query_type == "count":
            query, params = builder.build_count()
            result = await self._cm.fetch_one(query, tuple(params) if params else None)
            return result.get("count", 0) if result else 0
        else:
            raise ValueError(f"Unknown query type: {query_type}")


__all__ = ["WMysql", "AsyncWMysql"]
