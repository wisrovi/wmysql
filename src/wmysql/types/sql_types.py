from typing import Any, Dict, Type


class SQLType:
    pass


class Integer(SQLType):
    pass


class BigInteger(SQLType):
    pass


class SmallInteger(SQLType):
    pass


class TinyInteger(SQLType):
    pass


class Decimal(SQLType):
    pass


class Float(SQLType):
    pass


class Double(SQLType):
    pass


class Boolean(SQLType):
    pass


class Text(SQLType):
    pass


class String(SQLType):
    pass


class Char(SQLType):
    pass


class VarChar(SQLType):
    pass


class Date(SQLType):
    pass


class DateTime(SQLType):
    pass


class Timestamp(SQLType):
    pass


class Time(SQLType):
    pass


class Blob(SQLType):
    pass


class Json(SQLType):
    pass


class Enum(SQLType):
    pass


class Set(SQLType):
    pass


SQL_TYPE_MAP: Dict[Type[SQLType], str] = {
    Integer: "INT",
    BigInteger: "BIGINT",
    SmallInteger: "SMALLINT",
    TinyInteger: "TINYINT",
    Decimal: "DECIMAL(10,2)",
    Float: "FLOAT",
    Double: "DOUBLE",
    Boolean: "TINYINT(1)",
    Text: "TEXT",
    String: "VARCHAR(255)",
    Char: "CHAR(255)",
    VarChar: "VARCHAR(255)",
    Date: "DATE",
    DateTime: "DATETIME",
    Timestamp: "TIMESTAMP",
    Time: "TIME",
    Blob: "BLOB",
    Json: "JSON",
    Enum: "ENUM",
    Set: "SET",
}

PYTHON_TO_SQL_TYPE: Dict[str, str] = {
    "int": "INT",
    "bigint": "BIGINT",
    "smallint": "SMALLINT",
    "tinyint": "TINYINT",
    "float": "FLOAT",
    "double": "DOUBLE",
    "bool": "TINYINT(1)",
    "str": "VARCHAR(255)",
    "bytes": "BLOB",
    "date": "DATE",
    "datetime": "DATETIME",
    "time": "TIME",
    "list": "JSON",
    "dict": "JSON",
    "tuple": "JSON",
    "set": "JSON",
}


def get_sql_type(python_type: Any) -> str:
    type_name = type(python_type).__name__.lower()
    return PYTHON_TO_SQL_TYPE.get(type_name, "VARCHAR(255)")


__all__ = [
    "SQLType",
    "Integer",
    "BigInteger",
    "SmallInteger",
    "TinyInteger",
    "Decimal",
    "Float",
    "Double",
    "Boolean",
    "Text",
    "String",
    "Char",
    "VarChar",
    "Date",
    "DateTime",
    "Timestamp",
    "Time",
    "Blob",
    "Json",
    "Enum",
    "Set",
    "SQL_TYPE_MAP",
    "PYTHON_TO_SQL_TYPE",
    "get_sql_type",
]
