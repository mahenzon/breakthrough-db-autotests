import re
from typing import TYPE_CHECKING

import psycopg
from psycopg import sql as pg_sql
from psycopg.conninfo import make_conninfo

if TYPE_CHECKING:
    from testing.settings import Settings


def validate_database_for_tests_name(database_name: str) -> None:
    if not database_name.startswith("test_"):
        msg = f"testing db must start with 'test_'. Got: {database_name!r}."
        raise ValueError(msg)

    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", database_name):
        msg = (
            f"testing db must be a simple PostgreSQL identifier. Got: {database_name!r}."
        )
        raise ValueError(
            msg,
        )


def make_admin_conninfo(settings: Settings) -> str:
    return make_conninfo(
        host=settings.pg.host,
        port=settings.pg.port,
        user=settings.pg.user,
        password=settings.pg.password.get_secret_value(),
        dbname=settings.pg.admin_db,
    )


def make_conninfo_for_tests(settings: Settings) -> str:
    validate_database_for_tests_name(settings.pg.testing_db)

    return make_conninfo(
        host=settings.pg.host,
        port=settings.pg.port,
        user=settings.pg.user,
        password=settings.pg.password.get_secret_value(),
        dbname=settings.pg.testing_db,
    )


def database_exists(
    admin_conn: psycopg.Connection,
    database_name: str,
) -> bool:
    row = admin_conn.execute(
        """
        select 1
        from pg_database
        where datname = %s
        """,
        (database_name,),
    ).fetchone()

    return row is not None


def create_database(
    admin_conn: psycopg.Connection,
    database_name: str,
) -> None:
    validate_database_for_tests_name(database_name)

    admin_conn.execute(
        pg_sql.SQL("create database {}").format(
            pg_sql.Identifier(database_name),
        ),
    )


def ensure_database_exists(
    admin_conn: psycopg.Connection,
    database_name: str,
) -> None:
    validate_database_for_tests_name(database_name)

    if not database_exists(admin_conn, database_name):
        create_database(admin_conn, database_name)


def reset_public_schema(conn: psycopg.Connection) -> None:
    conn.execute("drop schema if exists public cascade")
    conn.execute("create schema public")
    conn.execute("grant usage, create on schema public to public")


def create_recipe_tables(conn: psycopg.Connection) -> None:
    conn.execute("""
        create table recipes (
            id serial primary key,
            title text not null,
            category text not null,
            cooking_time integer not null check (cooking_time > 0),
            extra_meta jsonb not null default '{}'::jsonb,
            created_at timestamp not null default now()
        )
        """)
