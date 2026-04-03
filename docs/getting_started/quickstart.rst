Quickstart
===========

This guide will help you get started with wmysql quickly.

Basic Usage
-----------

.. code-block:: python

    from wmysql import WMysql, ConnectionManager

    cm = ConnectionManager(
        host="localhost",
        port=3306,
        user="your_user",
        password="your_password",
        database="your_database"
    )

    db = WMysql(cm)

    result = db.fetch_all("users")
    print(result)

Insert Operations
-----------------

.. code-block:: python

    db.insert("users", {"name": "John", "email": "john@example.com"})

Update Operations
-----------------

.. code-block:: python

    db.update("users", {"name": "Jane"}, where={"id": 1})

Delete Operations
-----------------

.. code-block:: python

    db.delete("users", where={"id": 1})

QueryBuilder
------------

.. code-block:: python

    from wmysql import QueryBuilder

    query = (QueryBuilder()
        .select("*")
        .from_table("users")
        .where("active", "=", True)
        .order_by("created_at", "DESC")
        .build())

    results = db.execute(query)

Using TableSync
---------------

.. code-block:: python

    from wmysql import TableSync
    from pydantic import BaseModel

    class User(BaseModel):
        id: int | None = None
        name: str
        email: str

    sync = TableSync(cm)
    sync.sync_table(User, "users")