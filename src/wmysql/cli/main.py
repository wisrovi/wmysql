import click
import json
import sys
from typing import Optional

from wmysql import WMysql, ConnectionManager
from wmysql.builders import QueryBuilder


def get_connection(host, port, user, password, database):
    return ConnectionManager(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )


@click.group()
@click.option("--host", default="localhost", help="MySQL host")
@click.option("--port", default=3306, type=int, help="MySQL port")
@click.option("--user", default="root", help="MySQL user")
@click.option("--password", default="", help="MySQL password")
@click.option("--database", default="", help="MySQL database")
@click.pass_context
def cli(ctx, host, port, user, password, database):
    ctx.ensure_object(dict)
    ctx.obj["host"] = host
    ctx.obj["port"] = port
    ctx.obj["user"] = user
    ctx.obj["password"] = password
    ctx.obj["database"] = database


@cli.command()
@click.argument("table")
@click.argument("columns", nargs=-1)
@click.pass_context
def init(ctx, table, columns):
    if not columns:
        click.echo(
            "Error: Columns required (e.g., id INT PRIMARY KEY, name VARCHAR(255))"
        )
        sys.exit(1)

    cm = get_connection(
        ctx.obj["host"],
        ctx.obj["port"],
        ctx.obj["user"],
        ctx.obj["password"],
        ctx.obj["database"],
    )
    wmysql = WMysql(cm)

    try:
        col_defs = " ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table} ({col_defs})"
        wmysql.execute(query)
        click.echo(f"Table '{table}' created successfully")
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)
    finally:
        cm.close()


@cli.command("list")
@click.option("--limit", default=10, type=int, help="Limit results")
@click.pass_context
def list_tables(ctx, limit):
    cm = get_connection(
        ctx.obj["host"],
        ctx.obj["port"],
        ctx.obj["user"],
        ctx.obj["password"],
        ctx.obj["database"],
    )
    wmysql = WMysql(cm)

    try:
        tables = wmysql.raw_query("SHOW TABLES")
        database = cm.config.get("database", "")
        table_names = [row.get(f"Tables_in_{database}", "") for row in tables]

        for name in table_names[:limit]:
            click.echo(name)
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)
    finally:
        cm.close()


@cli.command()
@click.argument("table")
@click.argument("data", required=False)
@click.option("--json", "json_data", help="JSON data string")
@click.pass_context
def insert(ctx, table, data, json_data):
    if not data and not json_data:
        click.echo("Error: Data required (provide as positional arg or --json)")
        sys.exit(1)

    try:
        if json_data:
            insert_data = json.loads(json_data)
        else:
            insert_data = json.loads(data)
    except json.JSONDecodeError as e:
        click.echo(f"Error: Invalid JSON: {e}")
        sys.exit(1)

    cm = get_connection(
        ctx.obj["host"],
        ctx.obj["port"],
        ctx.obj["user"],
        ctx.obj["password"],
        ctx.obj["database"],
    )
    wmysql = WMysql(cm)

    try:
        wmysql.create(table, insert_data)
        click.echo("Row inserted successfully")
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)
    finally:
        cm.close()


@cli.command()
@click.argument("table")
@click.option("--filter", multiple=True, help="Filter as key=value")
@click.option("--columns", help="Comma-separated columns")
@click.option("--limit", default=1, type=int, help="Limit results")
@click.pass_context
def get(ctx, table, filter, columns, limit):
    filters = {}
    for f in filter:
        if "=" in f:
            k, v = f.split("=", 1)
            filters[k] = v

    col_list = columns.split(",") if columns else None

    cm = get_connection(
        ctx.obj["host"],
        ctx.obj["port"],
        ctx.obj["user"],
        ctx.obj["password"],
        ctx.obj["database"],
    )
    wmysql = WMysql(cm)

    try:
        if limit == 1:
            result = wmysql.get(table, filters, col_list)
            if result:
                click.echo(json.dumps(result, default=str, indent=2))
            else:
                click.echo("No results found")
        else:
            results = wmysql.get_all(table, filters, col_list, limit=limit)
            for r in results:
                click.echo(json.dumps(r, default=str, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)
    finally:
        cm.close()


@cli.command()
@click.argument("table")
@click.option("--filter", multiple=True, help="Filter as key=value")
@click.pass_context
def delete(ctx, table, filter):
    filters = {}
    for f in filter:
        if "=" in f:
            k, v = f.split("=", 1)
            filters[k] = v

    if not filters:
        click.echo("Error: At least one filter required")
        sys.exit(1)

    cm = get_connection(
        ctx.obj["host"],
        ctx.obj["port"],
        ctx.obj["user"],
        ctx.obj["password"],
        ctx.obj["database"],
    )
    wmysql = WMysql(cm)

    try:
        deleted = wmysql.delete(table, filters)
        click.echo(f"Deleted {deleted} row(s)")
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)
    finally:
        cm.close()


@cli.command()
@click.argument("table")
@click.option("--filter", multiple=True, help="Filter as key=value")
@click.pass_context
def count(ctx, table, filter):
    filters = {}
    for f in filter:
        if "=" in f:
            k, v = f.split("=", 1)
            filters[k] = v

    cm = get_connection(
        ctx.obj["host"],
        ctx.obj["port"],
        ctx.obj["user"],
        ctx.obj["password"],
        ctx.obj["database"],
    )
    wmysql = WMysql(cm)

    try:
        total = wmysql.count(table, filters)
        click.echo(f"Total rows: {total}")
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)
    finally:
        cm.close()


@cli.command()
@click.argument("table")
@click.confirmation_option(prompt="Are you sure you want to drop the table?")
@click.pass_context
def drop(ctx, table):
    cm = get_connection(
        ctx.obj["host"],
        ctx.obj["port"],
        ctx.obj["user"],
        ctx.obj["password"],
        ctx.obj["database"],
    )
    wmysql = WMysql(cm)

    try:
        wmysql.execute(f"DROP TABLE {table}")
        click.echo(f"Table '{table}' dropped successfully")
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)
    finally:
        cm.close()


if __name__ == "__main__":
    cli()
