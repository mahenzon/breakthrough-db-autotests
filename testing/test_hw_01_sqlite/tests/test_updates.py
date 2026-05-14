from typing import TYPE_CHECKING

import pytest

from testing.test_hw_01_sqlite import constants
from testing.test_hw_01_sqlite import dto
from testing.test_hw_01_sqlite import factories as f

import solutions.hw_01_sqlite as solution

if TYPE_CHECKING:
    import sqlite3

    from faker import Faker

pytestmark = pytest.mark.sqlite


def test_update_recipe_description_updates_existing_recipe(
    empty_db: sqlite3.Cursor,
    inserted_recipe: dto.InsertedRecipe,
    fake: Faker,
) -> None:
    title = inserted_recipe.data.title
    updated_description = fake.sentence()

    updated_count = solution.update_recipe_description(
        empty_db,
        title,
        updated_description,
    )

    assert updated_count == constants.EXPECTED_ONE_ROW

    row = solution.get_recipe_by_title(
        empty_db,
        title,
    )

    assert row is not None
    assert row[constants.COL_DESCRIPTION] == updated_description


def test_update_recipe_description_returns_zero_for_missing_recipe(
    empty_db: sqlite3.Cursor,
    recipe_factory: f.RecipeDataFactory,
    fake: Faker,
) -> None:
    missing_recipe = recipe_factory()
    updated_description = fake.sentence()

    updated_count = solution.update_recipe_description(
        empty_db,
        missing_recipe.title,
        updated_description,
    )

    assert updated_count == constants.EXPECTED_ZERO_ROWS


@pytest.mark.parametrize(
    "new_description",
    [
        "Short description",
        "Description with several words",
        "",
    ],
)
def test_update_recipe_description_accepts_different_descriptions(
    empty_db: sqlite3.Cursor,
    inserted_recipe: dto.InsertedRecipe,
    new_description: str,
) -> None:
    title = inserted_recipe.data.title

    updated_count = solution.update_recipe_description(
        empty_db,
        title,
        new_description,
    )

    row = solution.get_recipe_by_title(
        empty_db,
        title,
    )

    assert updated_count == constants.EXPECTED_ONE_ROW
    assert row is not None
    assert row[constants.COL_DESCRIPTION] == new_description
