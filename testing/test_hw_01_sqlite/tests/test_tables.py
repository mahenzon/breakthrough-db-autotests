from typing import TYPE_CHECKING

import pytest

from testing.test_hw_01_sqlite import constants

import solutions.hw_01_sqlite as solution

if TYPE_CHECKING:
    import sqlite3

pytestmark = pytest.mark.sqlite


def test_create_tables_creates_required_tables(
    cur: sqlite3.Cursor,
) -> None:
    solution.create_tables(cur, drop=True)

    result = cur.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = ?
        ORDER BY name
        """,
        (constants.TABLE_TYPE,),
    )

    table_names = {row[constants.COL_NAME] for row in result.fetchall()}

    assert constants.RECIPES_TABLE in table_names
    assert constants.INGREDIENTS_TABLE in table_names


def test_create_tables_can_be_called_more_than_once(
    cur: sqlite3.Cursor,
) -> None:
    solution.create_tables(cur, drop=True)
    solution.create_tables(cur)

    result = cur.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = ?
        ORDER BY name
        """,
        (constants.TABLE_TYPE,),
    )

    table_names = {row[constants.COL_NAME] for row in result.fetchall()}

    assert constants.RECIPES_TABLE in table_names
    assert constants.INGREDIENTS_TABLE in table_names
