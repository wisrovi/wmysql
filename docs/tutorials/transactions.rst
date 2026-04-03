Transactions
============

Transaction management in wmysql.

Basic Usage
-----------

.. code-block:: python

    from wmysql import WMysql, ConnectionManager, Transaction

    cm = ConnectionManager(
        host="localhost",
        user="your_user",
        password="your_password",
        database="your_database"
    )

    with Transaction(cm) as t:
        db = WMysql(t)
        db.insert("accounts", {"id": 1, "balance": 1000})
        db.insert("accounts", {"id": 2, "balance": 500})
        db.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        db.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")

Manual Control
--------------

.. code-block:: python

    t = Transaction(cm)
    try:
        db = WMysql(t)
        db.insert("logs", {"action": "test"})
        t.commit()
    except Exception as e:
        t.rollback()
        raise e