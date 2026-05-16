"""
Search tests.

`search_recipes_tstring()` should build optional filters and return
namedtuple rows sorted by id.
"""

from typing import TYPE_CHECKING

import pytest

from testing.test_hw_02_psycopg import dto
from testing.test_hw_02_psycopg.conftest import assert_recipes_table_exists
from testing.test_hw_02_psycopg.conftest import recipes_by_category
from testing.test_hw_02_psycopg.conftest import recipes_with_meta_key
from testing.test_hw_02_psycopg.conftest import recipes_with_time_range

import solutions.hw_02_psycopg as solution

if TYPE_CHECKING:
    import psycopg


pytestmark = pytest.mark.psycopg


def test_search_without_filters_returns_all_rows_as_namedtuples(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(),
    )

    assert len(rows) == len(seeded_recipes.recipes)

    assert [row.title for row in rows] == [
        recipe.title for recipe in seeded_recipes.recipes
    ]

    first_row = rows[0]

    assert hasattr(first_row, "id")
    assert hasattr(first_row, "title")
    assert hasattr(first_row, "category")
    assert hasattr(first_row, "cooking_time")
    assert hasattr(first_row, "extra_meta")


def test_search_filters_by_category(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            category=seeded_recipes.repeated_category,
        ),
    )

    expected_recipes = recipes_by_category(
        seeded_recipes,
        seeded_recipes.repeated_category,
    )

    assert [row.title for row in rows] == [recipe.title for recipe in expected_recipes]


def test_search_filters_by_title_part_case_insensitive(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    expected_recipe = seeded_recipes.recipes[1]
    title_part = expected_recipe.title.split()[-1].lower()

    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            title_part=title_part,
        ),
    )

    assert [row.title for row in rows] == [expected_recipe.title]


def test_search_filters_by_minutes_from(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    minutes_from = seeded_recipes.recipes[1].cooking_time

    expected_recipes = recipes_with_time_range(
        seeded_recipes.recipes,
        minutes_from=minutes_from,
    )

    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            minutes_from=minutes_from,
        ),
    )

    assert [row.title for row in rows] == [recipe.title for recipe in expected_recipes]


def test_search_filters_by_minutes_to(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    minutes_to = seeded_recipes.quick_limit

    expected_recipes = recipes_with_time_range(
        seeded_recipes.recipes,
        minutes_to=minutes_to,
    )

    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            minutes_to=minutes_to,
        ),
    )

    assert [row.title for row in rows] == [recipe.title for recipe in expected_recipes]


def test_search_filters_by_minutes_range(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    minutes_from = seeded_recipes.recipes[0].cooking_time
    minutes_to = seeded_recipes.recipes[4].cooking_time

    expected_recipes = recipes_with_time_range(
        seeded_recipes.recipes,
        minutes_from=minutes_from,
        minutes_to=minutes_to,
    )

    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            minutes_from=minutes_from,
            minutes_to=minutes_to,
        ),
    )

    assert [row.title for row in rows] == [recipe.title for recipe in expected_recipes]


def test_search_filters_by_required_meta_key(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    expected_recipes = recipes_with_meta_key(
        seeded_recipes.recipes,
        seeded_recipes.common_meta_key,
    )

    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            required_meta_key=seeded_recipes.common_meta_key,
        ),
    )

    assert [row.title for row in rows] == [recipe.title for recipe in expected_recipes]


def test_search_combines_filters(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    expected_recipe = seeded_recipes.recipes[0]

    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            category=expected_recipe.category,
            minutes_to=expected_recipe.cooking_time,
            required_meta_key=seeded_recipes.common_meta_key,
        ),
    )

    assert [row.title for row in rows] == [expected_recipe.title]


def test_search_combines_all_filters(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    expected_recipe = next(
        recipe
        for recipe in seeded_recipes.recipes
        if seeded_recipes.unique_meta_key in recipe.extra_meta
    )

    title_part = expected_recipe.title.split()[-1]

    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            title_part=title_part,
            category=expected_recipe.category,
            minutes_from=expected_recipe.cooking_time - 1,
            minutes_to=expected_recipe.cooking_time + 1,
            required_meta_key=seeded_recipes.unique_meta_key,
        ),
    )

    assert [row.title for row in rows] == [expected_recipe.title]


def test_search_returns_empty_list_when_no_match(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    impossible_minutes = (
        min(recipe.cooking_time for recipe in seeded_recipes.recipes) - 1
    )

    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            minutes_to=impossible_minutes,
        ),
    )

    assert rows == []


def test_search_is_safe_with_sql_like_title_part(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            title_part=seeded_recipes.suspicious_title_part,
        ),
    )

    assert rows == []
    assert_recipes_table_exists(conn)


def test_search_is_safe_with_sql_like_category(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            category=seeded_recipes.suspicious_category,
        ),
    )

    assert rows == []
    assert_recipes_table_exists(conn)


def test_search_is_safe_with_sql_like_meta_key(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    rows = solution.search_recipes_tstring(
        conn,
        dto.RecipeSearchDTO(
            required_meta_key=seeded_recipes.suspicious_meta_key,
        ),
    )

    assert rows == []
    assert_recipes_table_exists(conn)
