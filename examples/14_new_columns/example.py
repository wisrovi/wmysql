from typing import Optional
from pydantic import BaseModel
from wmysql import WMysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "testdb",
}


class User(BaseModel):
    id: int
    name: str
    age: int


def main():
    db = WMysql(User, DB_CONFIG)
    db.sync.create_if_not_exists()
    db.insert(User(id=1, name="Alice", age=25))
    print(f"Initial users: {db.get_all()}")


class UserExtended(BaseModel):
    id: int
    name: str
    age: int
    email: Optional[str] = None


def main_extended():
    db = WMysql(UserExtended, DB_CONFIG)
    db.sync.add_columns()
    db.insert(UserExtended(id=2, name="Bob", age=30, email="bob@example.com"))
    print(f"Users with new column: {db.get_all()}")


if __name__ == "__main__":
    main()
