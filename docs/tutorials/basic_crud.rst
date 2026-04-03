Basic CRUD Operations
======================

This tutorial covers Create, Read, Update, and Delete operations with wmysql.

Setup
-----

.. code-block:: python

    from wmysql import WMysql, ConnectionManager
    from pydantic import BaseModel

    cm = ConnectionManager(
        host="localhost",
        port=3306,
        user="your_user",
        password="your_password",
        database="your_database"
    )

    db = WMysql(cm)

Create
~~~~~~

.. code-block:: python

    db.insert("users", {"name": "Alice", "email": "alice@example.com"})

Read
~~~~

.. code-block:: python

    users = db.fetch_all("users")
    user = db.fetch_one("users", where={"id": 1})

Update
~~~~~~

.. code-block:: python

    db.update("users", {"name": "Bob"}, where={"id": 1})

Delete
~~~~~~

.. code-block:: python

    db.delete("users", where={"id": 1})