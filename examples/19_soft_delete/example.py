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
    id: int
    name: str
    deleted: Optional[int] = Field(default=0)


def main():
    db = WMysql(User, DB_CONFIG)
    db.sync.create_if_not_exists()

    db.insert(User(id=1, name="Alice"))
    db.insert(User(id=2, name="Bob"))

    print(f"Total: {db.count()}")
    user = db.get_by_field(id=1)[0]
    db.update(1, User(id=1, name=user.name, deleted=1))
    print(f"After soft delete: {db.count()}")


if __name__ == "__main__":
    main()
