from pydantic import BaseModel
from wmysql import WMysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "testdb",
}


class Author(BaseModel):
    id: int
    name: str


class Book(BaseModel):
    id: int
    title: str
    author_id: int


def main():
    author_db = WMysql(Author, DB_CONFIG)
    book_db = WMysql(Book, DB_CONFIG)

    author_db.sync.create_if_not_exists()
    book_db.sync.create_if_not_exists()

    author_db.insert(Author(id=1, name="Alice"))
    book_db.insert(Book(id=1, title="Book 1", author_id=1))

    print(f"Authors: {author_db.get_all()}")
    print(f"Books: {book_db.get_all()}")


if __name__ == "__main__":
    main()
