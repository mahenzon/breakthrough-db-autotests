"""
Dynamic column tests.

`select_dynamic_recipe_column()` should safely compose identifiers:

    select title, {column_name:i}
    from recipes
    order by {order_by_field:i}
"""

from typing import TYPE_CHECKING

import psycopg
import pytest

from testing.test_hw_02_psycopg.conftest import assert_recipes_table_exists

import solutions.hw_02_psycopg as solution

if TYPE_CHECKING:
    from testing.test_hw_02_psycopg import dto


pytestmark = pytest.mark.psycopg


def test_select_dynamic_recipe_column_can_select_cooking_time_and_sort_by_it(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.select_dynamic_recipe_column(
        conn,
        "cooking_time",
        order_by_field="cooking_time",
    )

    expected_recipes = sorted(
        seeded_recipes.recipes,
        key=lambda recipe: recipe.cooking_time,
    )

    assert rows == [
        {
            "title": recipe.title,
            "cooking_time": recipe.cooking_time,
        }
        for recipe in expected_recipes
    ]


def test_select_dynamic_recipe_column_can_select_extra_meta(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.select_dynamic_recipe_column(
        conn,
        "extra_meta",
        order_by_field="title",
    )

    expected_recipes = sorted(
        seeded_recipes.recipes,
        key=lambda recipe: recipe.title,
    )

    assert rows == [
        {
            "title": recipe.title,
            "extra_meta": recipe.extra_meta,
        }
        for recipe in expected_recipes
    ]


def test_select_dynamic_recipe_column_can_select_category(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.select_dynamic_recipe_column(
        conn,
        "category",
        order_by_field="title",
    )

    expected_recipes = sorted(
        seeded_recipes.recipes,
        key=lambda recipe: recipe.title,
    )

    assert rows == [
        {
            "title": recipe.title,
            "category": recipe.category,
        }
        for recipe in expected_recipes
    ]


@pytest.mark.usefixtures("seeded_recipes")
def test_select_dynamic_recipe_column_quotes_selected_identifier(
    conn: psycopg.Connection,
) -> None:
    bad_column_name = "category from recipes; drop table recipes; --"

    with pytest.raises(psycopg.errors.UndefinedColumn):
        solution.select_dynamic_recipe_column(conn, bad_column_name)

    conn.rollback()
    assert_recipes_table_exists(conn)


@pytest.mark.usefixtures("seeded_recipes")
def test_select_dynamic_recipe_column_quotes_order_by_identifier(
    conn: psycopg.Connection,
) -> None:
    bad_order_by = "id; drop table recipes; --"

    with pytest.raises(psycopg.errors.UndefinedColumn):
        solution.select_dynamic_recipe_column(
            conn,
            "category",
            order_by_field=bad_order_by,
        )

    conn.rollback()
    assert_recipes_table_exists(conn)
