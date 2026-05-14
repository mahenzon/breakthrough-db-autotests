import sqlite3
from typing import TYPE_CHECKING

import pytest

from testing.test_hw_01_sqlite import constants
from testing.test_hw_01_sqlite import dto
from testing.test_hw_01_sqlite import factories as f

import solutions.hw_01_sqlite as solution

if TYPE_CHECKING:
    from faker import Faker

pytestmark = pytest.mark.sqlite


def test_add_recipe_returns_id_and_inserts_recipe(
    empty_db: sqlite3.Cursor,
    recipe_factory: f.RecipeDataFactory,
) -> None:
    recipe = recipe_factory()

    recipe_id = solution.add_recipe(
        empty_db,
        recipe.title,
        recipe.description,
    )

    assert isinstance(recipe_id, int)

    row = empty_db.execute(
        """
        SELECT id, title, description
        FROM recipes
        WHERE id = ?
        """,
        (recipe_id,),
    ).fetchone()

    assert row is not None
    assert row[constants.COL_TITLE] == recipe.title
    assert row[constants.COL_DESCRIPTION] == recipe.description


def test_add_recipe_uses_default_description(
    empty_db: sqlite3.Cursor,
    recipe_without_description_factory: f.RecipeWithoutDescriptionFactory,
) -> None:
    recipe = recipe_without_description_factory()

    recipe_id = solution.add_recipe(
        empty_db,
        recipe.title,
    )

    row = empty_db.execute(
        """
        SELECT id, title, description
        FROM recipes
        WHERE id = ?
        """,
        (recipe_id,),
    ).fetchone()

    assert row is not None
    assert row[constants.COL_TITLE] == recipe.title
    assert row[constants.COL_DESCRIPTION] == recipe.description


def test_get_recipe_by_title_returns_recipe(
    empty_db: sqlite3.Cursor,
    inserted_recipe: dto.InsertedRecipe,
) -> None:
    row = solution.get_recipe_by_title(
        empty_db,
        inserted_recipe.data.title,
    )

    assert row is not None
    assert row[constants.COL_ID] == inserted_recipe.id
    assert row[constants.COL_TITLE] == inserted_recipe.data.title
    assert row[constants.COL_DESCRIPTION] == inserted_recipe.data.description


def test_get_recipe_by_title_returns_none_for_missing_recipe(
    empty_db: sqlite3.Cursor,
    recipe_factory: f.RecipeDataFactory,
) -> None:
    missing_recipe = recipe_factory()

    row = solution.get_recipe_by_title(
        empty_db,
        missing_recipe.title,
    )

    assert row is None


def test_recipe_title_must_be_unique(
    empty_db: sqlite3.Cursor,
    recipe_factory: f.RecipeDataFactory,
    fake: Faker,
) -> None:
    recipe = recipe_factory()
    some_description = fake.sentence()

    solution.add_recipe(
        empty_db,
        recipe.title,
        recipe.description,
    )

    with pytest.raises(sqlite3.IntegrityError):
        solution.add_recipe(
            empty_db,
            recipe.title,
            some_description,
        )


@pytest.mark.parametrize(
    "missing_title",
    [
        "Missing Recipe",
        "Unknown Recipe",
        "Recipe That Does Not Exist",
    ],
)
def test_get_recipe_by_title_returns_none_for_different_missing_titles(
    empty_db: sqlite3.Cursor,
    missing_title: str,
) -> None:
    row = solution.get_recipe_by_title(
        empty_db,
        missing_title,
    )

    assert row is None
