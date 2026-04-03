from pydantic import BaseModel
from wmysql import WMysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "testdb",
}


class Employee(BaseModel):
    id: int
    name: str
    department: str
    salary: float


def main():
    db = WMysql(Employee, DB_CONFIG)
    db.sync.create_if_not_exists()

    employees = [
        Employee(id=1, name="Alice", department="IT", salary=70000),
        Employee(id=2, name="Bob", department="IT", salary=75000),
    ]
    for emp in employees:
        db.insert(emp)

    result = db.execute_raw(
        "SELECT name, salary, ROW_NUMBER() OVER (ORDER BY salary DESC) as rn FROM employees"
    )
    print(f"Window function: {result}")

    db.close()


if __name__ == "__main__":
    main()
