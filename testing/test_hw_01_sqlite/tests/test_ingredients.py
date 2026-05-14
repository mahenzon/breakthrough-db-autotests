from typing import TYPE_CHECKING

import pytest

from testing.test_hw_01_sqlite import constants
from testing.test_hw_01_sqlite import dto
from testing.test_hw_01_sqlite import factories as f

import solutions.hw_01_sqlite as solution

if TYPE_CHECKING:
    import sqlite3

pytestmark = pytest.mark.sqlite


def test_add_ingredient_returns_id_and_inserts_ingredient(
    empty_db: sqlite3.Cursor,
    inserted_recipe: dto.InsertedRecipe,
    ingredient_factory: f.IngredientDataFactory,
) -> None:
    ingredient = ingredient_factory()

    ingredient_id = solution.add_ingredient(
        empty_db,
        inserted_recipe.id,
        ingredient.name,
        ingredient.quantity,
    )

    assert isinstance(ingredient_id, int)

    row = empty_db.execute(
        """
        SELECT id, recipe_id, name, quantity
        FROM ingredients
        WHERE id = ?
        """,
        (ingredient_id,),
    ).fetchone()

    assert row is not None
    assert row[constants.COL_RECIPE_ID] == inserted_recipe.id
    assert row[constants.COL_NAME] == ingredient.name
    assert row[constants.COL_QUANTITY] == ingredient.quantity


def test_add_ingredient_uses_default_quantity(
    empty_db: sqlite3.Cursor,
    inserted_recipe: dto.InsertedRecipe,
    ingredient_without_quantity_factory: f.IngredientWithoutQuantityFactory,
) -> None:
    ingredient = ingredient_without_quantity_factory()

    ingredient_id = solution.add_ingredient(
        empty_db,
        inserted_recipe.id,
        ingredient.name,
    )

    row = empty_db.execute(
        """
        SELECT id, recipe_id, name, quantity
        FROM ingredients
        WHERE id = ?
        """,
        (ingredient_id,),
    ).fetchone()

    assert row is not None
    assert row[constants.COL_NAME] == ingredient.name
    assert row[constants.COL_QUANTITY] == ingredient.quantity


def test_get_ingredients_for_recipe_returns_all_ingredients(
    empty_db: sqlite3.Cursor,
    inserted_recipe_with_ingredients: dto.InsertedRecipeWithIngredients,
) -> None:
    recipe_id = inserted_recipe_with_ingredients.recipe_id
    ingredient_ids = inserted_recipe_with_ingredients.ingredient_ids
    data = inserted_recipe_with_ingredients.data

    rows = solution.get_ingredients_for_recipe(
        empty_db,
        recipe_id,
    )

    assert len(rows) == len(data.ingredients)

    assert [row[constants.COL_ID] for row in rows] == ingredient_ids

    assert [row[constants.COL_NAME] for row in rows] == [
        ingredient.name for ingredient in data.ingredients
    ]

    assert [row[constants.COL_QUANTITY] for row in rows] == [
        ingredient.quantity for ingredient in data.ingredients
    ]


def test_get_ingredients_for_recipe_does_not_return_other_recipe_ingredients(
    empty_db: sqlite3.Cursor,
    two_inserted_recipes_with_ingredients: dto.TwoInsertedRecipesWIngredients,
) -> None:
    data = two_inserted_recipes_with_ingredients

    rows = solution.get_ingredients_for_recipe(
        empty_db,
        data.first_recipe_id,
    )

    assert len(rows) == constants.EXPECTED_ONE_ROW
    assert rows[0][constants.COL_NAME] == data.first_ingredient.name
    assert rows[0][constants.COL_QUANTITY] == data.first_ingredient.quantity


@pytest.mark.parametrize(
    "ingredient_count",
    [
        1,
        2,
        3,
    ],
)
def test_get_ingredients_for_recipe_returns_expected_number_of_rows(
    empty_db: sqlite3.Cursor,
    recipe_with_ingredients_factory: f.RecipeWithIngredientsFactory,
    ingredient_count: int,
) -> None:
    data = recipe_with_ingredients_factory(
        ingredient_count=ingredient_count,
    )

    recipe_id = solution.add_recipe(
        empty_db,
        data.recipe.title,
        data.recipe.description,
    )

    for ingredient in data.ingredients:
        solution.add_ingredient(
            empty_db,
            recipe_id,
            ingredient.name,
            ingredient.quantity,
        )

    rows = solution.get_ingredients_for_recipe(
        empty_db,
        recipe_id,
    )

    assert len(rows) == ingredient_count
