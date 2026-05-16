from typing import TYPE_CHECKING

import pytest

from testing.test_hw_02_psycopg.conftest import assert_recipes_table_exists
from testing.test_hw_02_psycopg.conftest import public_recipe_row
from testing.test_hw_02_psycopg.conftest import recipes_by_category
from testing.test_hw_02_psycopg.conftest import recipes_with_max_time

import solutions.hw_02_psycopg as solution

if TYPE_CHECKING:
    import psycopg

    from testing.test_hw_02_psycopg import dto

pytestmark = pytest.mark.psycopg


def test_filter_quick_recipes_returns_expected_rows_sorted(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    expected_recipes = recipes_with_max_time(
        recipes_by_category(seeded_recipes, seeded_recipes.repeated_category),
        seeded_recipes.medium_limit,
    )
    expected_recipes = sorted(
        expected_recipes,
        key=lambda recipe: recipe.cooking_time,
    )

    rows = solution.filter_quick_recipes(
        conn,
        category=seeded_recipes.repeated_category,
        max_minutes=seeded_recipes.medium_limit,
    )

    assert [
        {
            "title": row["title"],
            "category": row["category"],
            "cooking_time": row["cooking_time"],
        }
        for row in rows
    ] == [public_recipe_row(recipe) for recipe in expected_recipes]

    assert all("id" in row for row in rows)


def test_filter_quick_recipes_applies_max_minutes(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    expected_recipes = recipes_with_max_time(
        recipes_by_category(seeded_recipes, seeded_recipes.repeated_category),
        seeded_recipes.quick_limit,
    )

    rows = solution.filter_quick_recipes(
        conn,
        category=seeded_recipes.repeated_category,
        max_minutes=seeded_recipes.quick_limit,
    )

    assert [row["title"] for row in rows] == [
        recipe.title for recipe in expected_recipes
    ]


def test_filter_quick_recipes_with_no_results(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    smallest_time = min(recipe.cooking_time for recipe in seeded_recipes.recipes)

    rows = solution.filter_quick_recipes(
        conn,
        category=seeded_recipes.repeated_category,
        max_minutes=smallest_time - 1,
    )

    assert rows == []


def test_filter_quick_recipes_is_safe_with_sql_like_category(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.filter_quick_recipes(
        conn,
        category=seeded_recipes.suspicious_category,
        max_minutes=max(recipe.cooking_time for recipe in seeded_recipes.recipes),
    )

    assert rows == []
    assert_recipes_table_exists(conn)


def test_filter_quick_recipes_returns_dict_rows(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    expected_recipe = seeded_recipes.recipes[0]

    rows = solution.filter_quick_recipes(
        conn,
        category=expected_recipe.category,
        max_minutes=expected_recipe.cooking_time,
    )

    assert rows
    assert isinstance(rows[0], dict)
    assert set(rows[0]) == {"id", "title", "category", "cooking_time"}
