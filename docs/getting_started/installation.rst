Installation
============

Requirements
------------

* Python 3.8+
* PyMySQL library

Install via pip
---------------

.. code-block:: bash

    pip install wmysql

Install with development dependencies
-------------------------------------

.. code-block:: bash

    pip install wmysql[dev]

Install from source
-------------------

.. code-block:: bash

    git clone https://github.com/wisrovi/wmysql.git
    cd wmysql
    pip install -e .

Dependencies
~~~~~~~~~~~~

Required dependencies:

* ``pymysql>=1.0.0`` - Pure Python MySQL driver
* ``click>=8.0.0`` - Command-line interface framework

Optional dependencies:

* ``pytest>=7.0.0`` - Testing framework
* ``pytest-cov>=4.0.0`` - Coverage plugin
* ``pytest-asyncio>=0.21.0`` - Async test support