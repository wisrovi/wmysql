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


def main():
    db = WMysql(User, DB_CONFIG)
    db.sync.create_if_not_exists()
    db.insert(User(id=1, name="Alice"))

    result = db.execute_raw("SELECT COUNT(*) as cnt FROM user")
    print(f"Count: {result}")


if __name__ == "__main__":
    main()
