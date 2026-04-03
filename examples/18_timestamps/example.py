from datetime import datetime
from pydantic import BaseModel
from wmysql import WMysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "testdb",
}


class Record(BaseModel):
    id: int
    data: str
    created_at: str = datetime.now().isoformat()


def main():
    db = WMysql(Record, DB_CONFIG)
    db.sync.create_if_not_exists()
    db.insert(Record(id=1, data="Test"))
    record = db.get_by_field(id=1)[0]
    print(f"Record: {record}")


if __name__ == "__main__":
    main()
