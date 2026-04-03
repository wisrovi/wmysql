import pytest


class TestWMysqlImport:
    def test_import(self):
        from wmysql import WMysql

        assert WMysql is not None

    def test_version(self):
        import wmysql

        assert wmysql.__version__ == "1.0.0"


class TestQueryBuilder:
    def test_import(self):
        from wmysql import QueryBuilder

        qb = QueryBuilder().from_table("users")
        assert qb is not None


class TestExceptions:
    def test_import(self):
        from wmysql import WMysqlError

        with pytest.raises(WMysqlError):
            raise WMysqlError("test")
