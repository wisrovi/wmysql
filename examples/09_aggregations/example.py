from pydantic import BaseModel
from wmysql import WMysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "testdb",
}


class Order(BaseModel):
    id: int
    user_id: int
    amount: float


def main():
    db = WMysql(Order, DB_CONFIG)
    db.sync.create_if_not_exists()

    for i in range(1, 6):
        db.insert(Order(id=i, user_id=i, amount=float(i * 10)))

    total = db.aggregate("SUM", "amount")
    print(f"Total: {total}")

    count = db.aggregate("COUNT", "id")
    print(f"Count: {count}")

    avg = db.aggregate("AVG", "amount")
    print(f"Average: {avg}")

    db.close()


if __name__ == "__main__":
    main()
