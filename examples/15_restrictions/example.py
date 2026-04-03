from typing import Optional
from pydantic import BaseModel, Field
from wmysql import WMysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "testdb",
}


class User(BaseModel):
    id: int = Field(..., description="Primary Key")
    name: str = Field(..., description="NOT NULL")
    email: Optional[str] = Field(None, description="UNIQUE")


def main():
    db = WMysql(User, DB_CONFIG)
    db.sync.create_if_not_exists()

    print("=== INSERT VALID ===")
    db.insert(User(id=1, name="Alice", email="alice@example.com"))
    print(f"Count: {db.count()}")

    print("\n=== UNIQUE VIOLATION ===")
    try:
        db.insert(User(id=2, name="Bob", email="alice@example.com"))
    except Exception as e:
        print(f"Error: {e}")

    print("\n=== INSERT MORE ===")
    db.insert(User(id=2, name="Bob", email="bob@example.com"))
    print(f"Count: {db.count()}")


if __name__ == "__main__":
    main()
