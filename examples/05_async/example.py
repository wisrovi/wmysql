import asyncio
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
    email: str


async def main():
    db = WMysql(User, DB_CONFIG)
    await db.insert_async(User(id=3, name="Bob", email="bob@example.com"))
    users = await db.get_all_async()
    print(users)


if __name__ == "__main__":
    asyncio.run(main())
