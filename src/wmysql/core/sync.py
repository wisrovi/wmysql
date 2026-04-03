from typing import Any, Dict, List, Optional, Type
from wmysql.core.connection import ConnectionManager
from wmysql.types.sql_types import SQL_TYPE_MAP, SQLType


class TableSync:
    def __init__(self, connection_manager: ConnectionManager):
        self._cm = connection_manager

    def create_table(
        self,
        table_name: str,
        columns: Dict[str, Type[SQLType]],
        primary_key: str = "id",
        if_not_exists: bool = True,
    ) -> None:
        column_defs = []
        for col_name, col_type in columns.items():
            sql_type = SQL_TYPE_MAP.get(col_type, "VARCHAR(255)")
            if col_name == primary_key:
                column_defs.append(f"{col_name} {sql_type} AUTO_INCREMENT PRIMARY KEY")
            else:
                column_defs.append(f"{col_name} {sql_type}")

        if_not_exists_str = "IF NOT EXISTS " if if_not_exists else ""
        query = (
            f"CREATE TABLE {if_not_exists_str}{table_name} ({', '.join(column_defs)})"
        )

        self._cm.execute(query)
        self._cm.commit()

    def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        if_exists_str = "IF EXISTS " if if_exists else ""
        query = f"DROP TABLE {if_exists_str}{table_name}"
        self._cm.execute(query)
        self._cm.commit()

    def table_exists(self, table_name: str) -> bool:
        query = "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = %s AND table_name = %s"
        result = self._cm.fetch_one(
            query, (self._cm.config.get("database", ""), table_name)
        )
        return result and result.get("count", 0) > 0

    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        query = """
            SELECT column_name, data_type, character_maximum_length, is_nullable, column_key
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        return self._cm.fetch_all(
            query, (self._cm.config.get("database", ""), table_name)
        )

    def add_column(self, table_name: str, column_name: str, sql_type: str) -> None:
        query = f"ALTER TABLE {table_name} ADD {column_name} {sql_type}"
        self._cm.execute(query)
        self._cm.commit()

    def drop_column(self, table_name: str, column_name: str) -> None:
        query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        self._cm.execute(query)
        self._cm.commit()

    def modify_column(self, table_name: str, column_name: str, sql_type: str) -> None:
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {sql_type}"
        self._cm.execute(query)
        self._cm.commit()

    def rename_table(self, old_name: str, new_name: str) -> None:
        query = f"RENAME TABLE {old_name} TO {new_name}"
        self._cm.execute(query)
        self._cm.commit()

    def get_all_tables(self) -> List[str]:
        query = "SHOW TABLES"
        result = self._cm.fetch_all(query)
        database = self._cm.config.get("database", "")
        return [row.get(f"Tables_in_{database}", "") for row in result]


class AsyncTableSync:
    def __init__(self, connection_manager: ConnectionManager):
        self._cm = connection_manager

    async def create_table(
        self,
        table_name: str,
        columns: Dict[str, Type[SQLType]],
        primary_key: str = "id",
        if_not_exists: bool = True,
    ) -> None:
        column_defs = []
        for col_name, col_type in columns.items():
            sql_type = SQL_TYPE_MAP.get(col_type, "VARCHAR(255)")
            if col_name == primary_key:
                column_defs.append(f"{col_name} {sql_type} AUTO_INCREMENT PRIMARY KEY")
            else:
                column_defs.append(f"{col_name} {sql_type}")

        if_not_exists_str = "IF NOT EXISTS " if if_not_exists else ""
        query = (
            f"CREATE TABLE {if_not_exists_str}{table_name} ({', '.join(column_defs)})"
        )

        await self._cm.execute(query)
        await self._cm.commit()

    async def drop_table(self, table_name: str, if_exists: bool = True) -> None:
        if_exists_str = "IF EXISTS " if if_exists else ""
        query = f"DROP TABLE {if_exists_str}{table_name}"
        await self._cm.execute(query)
        await self._cm.commit()

    async def table_exists(self, table_name: str) -> bool:
        query = "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = %s AND table_name = %s"
        result = await self._cm.fetch_one(
            query, (self._cm.config.get("database", ""), table_name)
        )
        return result and result.get("count", 0) > 0

    async def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        query = """
            SELECT column_name, data_type, character_maximum_length, is_nullable, column_key
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        return await self._cm.fetch_all(
            query, (self._cm.config.get("database", ""), table_name)
        )

    async def add_column(
        self, table_name: str, column_name: str, sql_type: str
    ) -> None:
        query = f"ALTER TABLE {table_name} ADD {column_name} {sql_type}"
        await self._cm.execute(query)
        await self._cm.commit()

    async def drop_column(self, table_name: str, column_name: str) -> None:
        query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
        await self._cm.execute(query)
        await self._cm.commit()

    async def modify_column(
        self, table_name: str, column_name: str, sql_type: str
    ) -> None:
        query = f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {sql_type}"
        await self._cm.execute(query)
        await self._cm.commit()

    async def rename_table(self, old_name: str, new_name: str) -> None:
        query = f"RENAME TABLE {old_name} TO {new_name}"
        await self._cm.execute(query)
        await self._cm.commit()

    async def get_all_tables(self) -> List[str]:
        query = "SHOW TABLES"
        result = await self._cm.fetch_all(query)
        database = self._cm.config.get("database", "")
        return [row.get(f"Tables_in_{database}", "") for row in result]


__all__ = ["TableSync", "AsyncTableSync"]
