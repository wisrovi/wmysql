# wmysql

**MySQL ORM using Pydantic models - simple, type-safe database operations**

High-level Python ORM library providing a clean, type-safe interface for MySQL database operations using Pydantic models for schema definition.

## Key Features

- **Pydantic Integration** - Define database schema using Pydantic v2 models
- **Auto Table Creation** - Tables created/synchronized automatically with model changes
- **CRUD Operations** - Simple insert, get, update, delete methods
- **Column Sync** - Automatically adds new columns when model changes
- **Constraints Support** - Primary Key, UNIQUE, NOT NULL, Foreign Keys
- **Type Safety** - Full type hints and Pydantic validation
- **Async Support** - Full async/await for high-performance applications
- **Query Builder** - Safe query construction with SQL injection prevention
- **CLI Tool** - Command-line interface for common operations
- **Code Quality** - Pylint compatible, comprehensive type hints

## Technical Stack

- **Python**: 3.8+
- **Key Libraries**: pymysql>=1.0.0, click>=8.0.0
- **Testing**: pytest, pytest-cov, pytest-asyncio

## Installation & Setup

```bash
pip install wmysql
```

Development installation:
```bash
pip install -e ".[dev]"
```

## Architecture & Workflow

```
wmysql/
├── src/wmysql/           # Main library package
│   ├── core/            # Core database operations
│   ├── builders/        # SQL query builder
│   ├── exceptions/      # Custom exceptions
│   ├── types/           # SQL type mapping
│   └── cli/             # CLI tool
├── examples/            # Usage examples (13+ folders)
├── test/                # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docs/                # Sphinx documentation
├── stress_test/        # Performance testing
├── docker/             # Docker configurations
├── pyproject.toml      # Project config
└── README.md
```

**Workflow**: Define Pydantic model → Configure MySQL connection → Initialize WMysql → Auto table creation → Perform CRUD operations

## Configuration

**Environment Variables**:
- `WMYSQL_HOST` - Database host
- `WMYSQL_PORT` - Database port (default: 3306)
- `WMYSQL_USER` - Database user
- `WMYSQL_PASSWORD` - Database password
- `WMYSQL_DATABASE` - Database name

**Configuration Files**:
- `pyproject.toml` - Project metadata and dependencies
- `setup.py` - Package configuration

## Usage

```python
from pydantic import BaseModel
from wmysql import WMysql

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "mydb",
}

class User(BaseModel):
    id: int
    name: str
    email: str

db = WMysql(User, DB_CONFIG)
db.insert(User(id=1, name="John", email="john@example.com"))
users = db.get_all()
```

## Author

- **William Rodríguez** - [wisrovi.rodriguez@gmail.com](mailto:wisrovi.rodriguez@gmail.com)
- [LinkedIn](https://www.linkedin.com/in/wisrovi/)