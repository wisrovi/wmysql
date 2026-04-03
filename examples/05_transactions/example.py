from pydantic import BaseModel
from wmysql import WMysql, get_transaction

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
    email: str


def main():
    db = WMysql(User, DB_CONFIG)
    db.sync.create_if_not_exists()

    db.insert(User(id=1, name="Alice", email="alice@example.com"))

    def transactional_op(tx):
        db.update(User(id=1, name="Alice Updated", email="alice.updated@example.com"))
        return True

    result = db.with_transaction(transactional_op)
    print(f"Transaction committed: {result}")

    db.close()


if __name__ == "__main__":
    main()
