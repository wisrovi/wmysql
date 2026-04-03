import pytest
from wmysql.builders.query_builder import validate_identifier
from wmysql.exceptions import SQLInjectionError


class TestValidateIdentifier:
    def test_valid_identifier(self):
        validate_identifier("users")
        validate_identifier("my_table")
        validate_identifier("table123")

    def test_invalid_identifier(self):
        with pytest.raises(SQLInjectionError):
            validate_identifier("users; DROP TABLE")
        with pytest.raises(SQLInjectionError):
            validate_identifier("123table")
        with pytest.raises(SQLInjectionError):
            validate_identifier("my-table")
