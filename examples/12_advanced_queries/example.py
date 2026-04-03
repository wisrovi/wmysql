from pydantic import BaseModel
from wmysql import WMysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "testdb",
}


class Product(BaseModel):
    id: int
    name: str
    price: float


def main():
    db = WMysql(Product, DB_CONFIG)
    db.sync.create_if_not_exists()

    products = [
        Product(id=1, name="Laptop", price=999.99),
        Product(id=2, name="Mouse", price=29.99),
        Product(id=3, name="Keyboard", price=89.99),
    ]
    for p in products:
        db.insert(p)

    result = db.execute_raw(
        "SELECT * FROM products WHERE price > (SELECT AVG(price) FROM products)"
    )
    print(f"Above average: {result}")

    db.close()


if __name__ == "__main__":
    main()
