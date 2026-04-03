from typing import Any, Dict, List, Optional, Tuple, Union
from wmysql.types.sql_types import get_sql_type


class QueryBuilder:
    def __init__(self):
        self._query_parts: Dict[str, Any] = {
            "select": [],
            "from": None,
            "join": [],
            "where": [],
            "group_by": [],
            "having": [],
            "order_by": [],
            "limit_val": None,
            "offset_val": None,
            "insert_values": [],
            "update_values": {},
            "set": [],
        }
        self._params: List[Any] = []

    def select(self, *columns: str) -> "QueryBuilder":
        if not columns:
            self._query_parts["select"] = ["*"]
        else:
            self._query_parts["select"] = list(columns)
        return self

    def from_table(self, table: str) -> "QueryBuilder":
        self._query_parts["from"] = table
        return self

    def join(
        self, table: str, condition: str, join_type: str = "INNER"
    ) -> "QueryBuilder":
        self._query_parts["join"].append(
            {
                "type": join_type,
                "table": table,
                "condition": condition,
            }
        )
        return self

    def left_join(self, table: str, condition: str) -> "QueryBuilder":
        return self.join(table, condition, "LEFT")

    def right_join(self, table: str, condition: str) -> "QueryBuilder":
        return self.join(table, condition, "RIGHT")

    def where(self, condition: str, *params: Any) -> "QueryBuilder":
        self._query_parts["where"].append(condition)
        self._params.extend(params)
        return self

    def where_and(self, condition: str, *params: Any) -> "QueryBuilder":
        if self._query_parts["where"]:
            self._query_parts["where"][-1] += f" AND {condition}"
            self._params.extend(params)
        return self

    def where_or(self, condition: str, *params: Any) -> "QueryBuilder":
        if self._query_parts["where"]:
            self._query_parts["where"][-1] += f" OR {condition}"
            self._params.extend(params)
        return self

    def group_by(self, *columns: str) -> "QueryBuilder":
        self._query_parts["group_by"] = list(columns)
        return self

    def having(self, condition: str, *params: Any) -> "QueryBuilder":
        self._query_parts["having"].append(condition)
        self._params.extend(params)
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        self._query_parts["order_by"].append(f"{column} {direction}")
        return self

    def limit(self, count: int, offset: Optional[int] = None) -> "QueryBuilder":
        self._query_parts["limit_val"] = count
        if offset is not None:
            self._query_parts["offset_val"] = offset
        return self

    def offset(self, offset: int) -> "QueryBuilder":
        self._query_parts["offset_val"] = offset
        return self

    def insert(self, table: str, data: Dict[str, Any]) -> "QueryBuilder":
        self._query_parts["from"] = table
        self._query_parts["insert_values"] = [data]
        return self

    def bulk_insert(self, table: str, data: List[Dict[str, Any]]) -> "QueryBuilder":
        self._query_parts["from"] = table
        self._query_parts["insert_values"] = data
        return self

    def update(self, table: str, data: Dict[str, Any]) -> "QueryBuilder":
        self._query_parts["from"] = table
        self._query_parts["update_values"] = data
        return self

    def delete(self, table: str) -> "QueryBuilder":
        self._query_parts["from"] = table
        self._query_parts["delete"] = True
        return self

    def build_select(self) -> Tuple[str, List[Any]]:
        query_parts = []
        select_cols = ", ".join(self._query_parts["select"])
        query_parts.append(f"SELECT {select_cols}")

        if self._query_parts["from"]:
            query_parts.append(f"FROM {self._query_parts['from']}")

        for join in self._query_parts["join"]:
            query_parts.append(
                f"{join['type']} JOIN {join['table']} ON {join['condition']}"
            )

        if self._query_parts["where"]:
            where_str = " AND ".join(self._query_parts["where"])
            query_parts.append(f"WHERE {where_str}")

        if self._query_parts["group_by"]:
            query_parts.append(f"GROUP BY {', '.join(self._query_parts['group_by'])}")

        if self._query_parts["having"]:
            having_str = " AND ".join(self._query_parts["having"])
            query_parts.append(f"HAVING {having_str}")

        if self._query_parts["order_by"]:
            query_parts.append(f"ORDER BY {', '.join(self._query_parts['order_by'])}")

        if self._query_parts["limit_val"]:
            query_parts.append(f"LIMIT {self._query_parts['limit_val']}")
            if self._query_parts["offset_val"]:
                query_parts.append(f"OFFSET {self._query_parts['offset_val']}")

        return " ".join(query_parts), self._params.copy()

    def build_insert(self) -> Tuple[str, List[Any]]:
        if not self._query_parts["insert_values"]:
            raise ValueError("No values to insert")

        data = self._query_parts["insert_values"][0]
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())

        query = f"INSERT INTO {self._query_parts['from']} ({columns}) VALUES ({placeholders})"
        return query, values

    def build_bulk_insert(self) -> Tuple[str, List[Any]]:
        if not self._query_parts["insert_values"]:
            raise ValueError("No values to insert")

        data_list = self._query_parts["insert_values"]
        columns = ", ".join(data_list[0].keys())
        placeholders_list = []
        values = []

        for data in data_list:
            placeholders_list.append("(" + ", ".join(["%s"] * len(data)) + ")")
            values.extend(data.values())

        placeholders = ", ".join(placeholders_list)
        query = (
            f"INSERT INTO {self._query_parts['from']} ({columns}) VALUES {placeholders}"
        )
        return query, values

    def build_update(self) -> Tuple[str, List[Any]]:
        if not self._query_parts["update_values"]:
            raise ValueError("No values to update")

        set_parts = [f"{key} = %s" for key in self._query_parts["update_values"].keys()]
        set_clause = ", ".join(set_parts)
        values = list(self._query_parts["update_values"].values())
        values.extend(self._params)

        query = f"UPDATE {self._query_parts['from']} SET {set_clause}"
        if self._query_parts["where"]:
            where_str = " AND ".join(self._query_parts["where"])
            query += f" WHERE {where_str}"

        return query, values

    def build_delete(self) -> Tuple[str, List[Any]]:
        query = f"DELETE FROM {self._query_parts['from']}"
        if self._query_parts["where"]:
            where_str = " AND ".join(self._query_parts["where"])
            query += f" WHERE {where_str}"
        return query, self._params.copy()

    def build_count(self) -> Tuple[str, List[Any]]:
        query_parts = ["SELECT COUNT(*) as count"]
        query_parts.append(f"FROM {self._query_parts['from']}")

        if self._query_parts["where"]:
            where_str = " AND ".join(self._query_parts["where"])
            query_parts.append(f"WHERE {where_str}")

        return " ".join(query_parts), self._params.copy()

    def reset(self) -> None:
        self._query_parts = {
            "select": [],
            "from": None,
            "join": [],
            "where": [],
            "group_by": [],
            "having": [],
            "order_by": [],
            "limit_val": None,
            "offset_val": None,
            "insert_values": [],
            "update_values": {},
            "set": [],
        }
        self._params = []


__all__ = ["QueryBuilder"]
