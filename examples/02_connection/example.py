from wmysql import ConnectionManager

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "testdb",
}


def main():
    cm = ConnectionManager(**DB_CONFIG)
    with cm.get_connection() as conn:
        print(f"Connected: {conn is not None}")
    cm.close()


if __name__ == "__main__":
    main()
