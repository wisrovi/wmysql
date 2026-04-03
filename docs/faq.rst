FAQ
===

Frequently Asked Questions about wmysql.

General
-------

What is wmysql?
~~~~~~~~~~~~~~~

wmysql is a Python ORM library for MySQL providing connection management, query building, and CRUD operations.

What Python versions are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

wmysql supports Python 3.8 and later.

Connection
----------

How do I configure the connection?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wmysql import ConnectionManager

    cm = ConnectionManager(
        host="localhost",
        port=3306,
        user="your_user",
        password="your_password",
        database="your_database"
    )

Does wmysql support connection pooling?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, configure pool settings in ConnectionManager.

Transactions
------------

How do I use transactions?
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from wmysql import Transaction

    with Transaction(cm) as t:
        db = WMysql(t)
        db.insert("table1", data)

Errors
------

What exceptions does wmysql raise?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``WMysqlError`` - Base exception
- ``ConnectionError`` - Connection failures
- ``QueryError`` - Query execution errors
- ``ValidationError`` - Data validation errors
- ``TransactionError`` - Transaction failures