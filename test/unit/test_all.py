"""
Comprehensive test suite for wmysql library.
"""

import pytest
from unittest.mock import Mock, patch


class TestWMysqlImport:
    """Test basic imports."""

    def test_import_main_class(self):
        from wmysql import WMysql

        assert WMysql is not None

    def test_import_query_builder(self):
        from wmysql import QueryBuilder

        assert QueryBuilder is not None

    def test_import_table_sync(self):
        from wmysql import TableSync

        assert TableSync is not None

    def test_version(self):
        import wmysql

        assert wmysql.__version__ == "1.0.0"


class TestExceptions:
    """Test exception hierarchy."""

    def test_wmysql_error(self):
        from wmysql import WMysqlError

        with pytest.raises(WMysqlError):
            raise WMysqlError("test")

    def test_connection_error(self):
        from wmysql import ConnectionError

        with pytest.raises(ConnectionError):
            raise ConnectionError("test")

    def test_query_error(self):
        from wmysql import QueryError

        with pytest.raises(QueryError):
            raise QueryError("test")

    def test_validation_error(self):
        from wmysql import ValidationError

        with pytest.raises(ValidationError):
            raise ValidationError("test")

    def test_transaction_error(self):
        from wmysql import TransactionError

        with pytest.raises(TransactionError):
            raise TransactionError("test")

    def test_sync_error(self):
        from wmysql import SyncError

        with pytest.raises(SyncError):
            raise SyncError("test")

    def test_hierarchy(self):
        from wmysql import WMysqlError, ConnectionError, QueryError

        assert issubclass(ConnectionError, WMysqlError)
        assert issubclass(QueryError, WMysqlError)


class TestQueryBuilder:
    """Test QueryBuilder."""

    def test_fluent_api(self):
        from wmysql import QueryBuilder

        qb = QueryBuilder().select("*").from_table("users")
        assert qb is not None

    def test_where(self):
        from wmysql import QueryBuilder

        qb = QueryBuilder().select("*").from_table("users").where("id", "=", 1)
        query, _ = qb.build_select()
        assert "WHERE id = 1" in query

    def test_order_by(self):
        from wmysql import QueryBuilder

        qb = QueryBuilder().select("*").from_table("users").order_by("name")
        query, _ = qb.build_select()
        assert "ORDER BY name" in query

    def test_limit_offset(self):
        from wmysql import QueryBuilder

        qb = QueryBuilder().select("*").from_table("users").limit(10).offset(20)
        query, _ = qb.build_select()
        assert "LIMIT 10" in query
        assert "OFFSET 20" in query


class TestConnectionManager:
    """Test ConnectionManager."""

    def test_init(self):
        from wmysql import ConnectionManager

        cm = ConnectionManager({"host": "localhost", "port": 3306})
        assert cm is not None

    def test_thread_local(self):
        from wmysql import ConnectionManager

        cm = ConnectionManager({"host": "localhost"})
        assert hasattr(cm, "_thread_local")


class TestSqlTypes:
    """Test SQL type mapping."""

    def test_integer_type(self):
        from wmysql.types import get_sql_type
        from pydantic import BaseModel, Field

        class TestModel(BaseModel):
            id: int

        sql_type = get_sql_type(TestModel.model_fields["id"])
        assert "INTEGER" in sql_type

    def test_string_type(self):
        from wmysql.types import get_sql_type
        from pydantic import BaseModel

        class TestModel(BaseModel):
            name: str

        sql_type = get_sql_type(TestModel.model_fields["name"])
        assert "VARCHAR" in sql_type

    def test_boolean_type(self):
        from wmysql.types import get_sql_type
        from pydantic import BaseModel

        class TestModel(BaseModel):
            active: bool

        sql_type = get_sql_type(TestModel.model_fields["active"])
        assert "TINYINT" in sql_type

    def test_constraints(self):
        from wmysql.types import get_sql_type
        from pydantic import BaseModel, Field

        class TestModel(BaseModel):
            id: int = Field(..., description="Primary Key")
            email: str = Field(None, description="UNIQUE")

        id_type = get_sql_type(TestModel.model_fields["id"])
        email_type = get_sql_type(TestModel.model_fields["email"])

        assert "PRIMARY KEY" in id_type
        assert "UNIQUE" in email_type
