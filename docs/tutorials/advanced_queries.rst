Advanced Queries
=================

Advanced query operations using QueryBuilder.

Joins
-----

.. code-block:: python

    query = (QueryBuilder()
        .select("u.id", "u.name", "o.total")
        .from_table("users", "u")
        .join("orders", "o", "u.id = o.user_id")
        .build())

Aggregations
------------

.. code-block:: python

    query = (QueryBuilder()
        .select("COUNT(*)", "SUM(total)", "AVG(total)")
        .from_table("orders")
        .group_by("user_id")
        .build())

Subqueries
---------

.. code-block:: python

    query = (QueryBuilder()
        .select("*")
        .from_table("users")
        .where_in("id",
            QueryBuilder()
            .select("user_id")
            .from_table("orders")
            .where("total", ">", 100)
            .build()
        )
        .build())