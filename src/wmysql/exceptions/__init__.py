class WMysqlError(Exception):
    pass


class ConnectionError(WMysqlError):
    pass


class QueryError(WMysqlError):
    pass


class ValidationError(WMysqlError):
    pass


class TransactionError(WMysqlError):
    pass


class SyncError(WMysqlError):
    pass


__all__ = [
    "WMysqlError",
    "ConnectionError",
    "QueryError",
    "ValidationError",
    "TransactionError",
    "SyncError",
]
