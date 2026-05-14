from typing import TYPE_CHECKING

import pytest

from testing.test_hw_01_sqlite import constants
from testing.test_hw_01_sqlite import dto
from testing.test_hw_01_sqlite import factories as f

import solutions.hw_01_sqlite as solution

if TYPE_CHECKING:
    import sqlite3

pytestmark = pytest.mark.sqlite


def test_delete_recipe_deletes_existing_recipe(
    empty_db: sqlite3.Cursor,
    inserted_recipe: dto.InsertedRecipe,
) -> None:
    title = inserted_recipe.data.title

    deleted_count = solution.delete_recipe(
        empty_db,
        title,
    )

    assert deleted_count == constants.EXPECTED_ONE_ROW

    row = solution.get_recipe_by_title(
        empty_db,
        title,
    )

    assert row is None


def test_delete_recipe_returns_zero_for_missing_recipe(
    empty_db: sqlite3.Cursor,
    recipe_factory: f.RecipeDataFactory,
) -> None:
    missing_recipe = recipe_factory()

    deleted_count = solution.delete_recipe(
        empty_db,
        missing_recipe.title,
    )

    assert deleted_count == constants.EXPECTED_ZERO_ROWS


def test_delete_recipe_also_deletes_ingredients(
    empty_db: sqlite3.Cursor,
    inserted_recipe_with_ingredients: dto.InsertedRecipeWithIngredients,
) -> None:
    recipe_id = inserted_recipe_with_ingredients.recipe_id
    title = inserted_recipe_with_ingredients.data.recipe.title

    deleted_count = solution.delete_recipe(
        empty_db,
        title,
    )

    assert deleted_count == constants.EXPECTED_ONE_ROW

    ingredient_rows = empty_db.execute(
        """
        SELECT id
        FROM ingredients
        WHERE recipe_id = ?
        """,
        (recipe_id,),
    ).fetchall()

    assert ingredient_rows == []


@pytest.mark.parametrize(
    "missing_title",
    [
        "Missing Recipe",
        "Unknown Recipe",
        "Recipe That Does Not Exist",
    ],
)
def test_delete_recipe_returns_zero_for_different_missing_titles(
    empty_db: sqlite3.Cursor,
    missing_title: str,
) -> None:
    deleted_count = solution.delete_recipe(
        empty_db,
        missing_title,
    )

    assert deleted_count == constants.EXPECTED_ZERO_ROWS
