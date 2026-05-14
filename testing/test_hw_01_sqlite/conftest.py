import sqlite3
from typing import TYPE_CHECKING

import pytest
from faker import Faker

from testing.test_hw_01_sqlite import constants
from testing.test_hw_01_sqlite import dto
from testing.test_hw_01_sqlite import factories

import solutions.hw_01_sqlite as solution

if TYPE_CHECKING:
    from collections.abc import Generator

pytestmark = pytest.mark.sqlite


@pytest.fixture(scope="session")
def fake() -> Faker:
    faker = Faker()
    Faker.seed("foo-bar-constant-seed-here-to-make-reproducible-tests")
    return faker


@pytest.fixture
def conn() -> Generator[sqlite3.Connection]:
    connection = sqlite3.connect(constants.IN_MEMORY_DB)
    connection.row_factory = sqlite3.Row
    connection.execute(constants.FOREIGN_KEYS_ON_SQL)

    yield connection

    connection.close()


@pytest.fixture
def cur(conn: sqlite3.Connection) -> sqlite3.Cursor:
    return conn.cursor()


@pytest.fixture
def empty_db(cur: sqlite3.Cursor) -> sqlite3.Cursor:
    solution.create_tables(cur, drop=True)
    return cur


@pytest.fixture
def recipe_factory(fake: Faker) -> factories.RecipeDataFactory:
    return factories.RecipeDataFactory(fake)


@pytest.fixture
def recipe_without_description_factory(
    fake: Faker,
) -> factories.RecipeWithoutDescriptionFactory:
    return factories.RecipeWithoutDescriptionFactory(fake)


@pytest.fixture
def ingredient_factory(fake: Faker) -> factories.IngredientDataFactory:
    return factories.IngredientDataFactory(fake)


@pytest.fixture
def ingredient_without_quantity_factory(
    fake: Faker,
) -> factories.IngredientWithoutQuantityFactory:
    return factories.IngredientWithoutQuantityFactory(fake)


@pytest.fixture
def recipe_with_ingredients_factory(
    recipe_factory: factories.RecipeDataFactory,
    ingredient_factory: factories.IngredientDataFactory,
) -> factories.RecipeWithIngredientsFactory:
    return factories.RecipeWithIngredientsFactory(
        recipe_factory=recipe_factory,
        ingredient_factory=ingredient_factory,
    )


@pytest.fixture
def inserted_recipe(
    empty_db: sqlite3.Cursor,
    recipe_factory: factories.RecipeDataFactory,
) -> dto.InsertedRecipe:
    recipe = recipe_factory()

    recipe_id = solution.add_recipe(
        empty_db,
        recipe.title,
        recipe.description,
    )

    return dto.InsertedRecipe(
        id=recipe_id,
        data=recipe,
    )


@pytest.fixture
def inserted_recipe_without_description(
    empty_db: sqlite3.Cursor,
    recipe_without_description_factory: factories.RecipeWoDescriptionFactory,
) -> dto.InsertedRecipe:
    recipe = recipe_without_description_factory()

    recipe_id = solution.add_recipe(
        empty_db,
        recipe.title,
    )

    return dto.InsertedRecipe(
        id=recipe_id,
        data=recipe,
    )


@pytest.fixture
def inserted_recipe_with_ingredients(
    empty_db: sqlite3.Cursor,
    recipe_with_ingredients_factory: factories.RecipeWithIngredientsFactory,
) -> dto.InsertedRecipeWithIngredients:
    data = recipe_with_ingredients_factory()

    recipe_id = solution.add_recipe(
        empty_db,
        data.recipe.title,
        data.recipe.description,
    )

    ingredient_ids: list[int] = []

    for ingredient in data.ingredients:
        ingredient_id = solution.add_ingredient(
            empty_db,
            recipe_id,
            ingredient.name,
            ingredient.quantity,
        )
        ingredient_ids.append(ingredient_id)

    return dto.InsertedRecipeWithIngredients(
        recipe_id=recipe_id,
        ingredient_ids=ingredient_ids,
        data=data,
    )


@pytest.fixture
def two_inserted_recipes_with_ingredients(
    empty_db: sqlite3.Cursor,
    recipe_factory: factories.RecipeDataFactory,
    ingredient_factory: factories.IngredientDataFactory,
) -> dto.TwoInsertedRecipesWithIngredients:
    first_recipe = recipe_factory()
    second_recipe = recipe_factory()

    first_ingredient = ingredient_factory()
    second_ingredient = ingredient_factory()

    first_recipe_id = solution.add_recipe(
        empty_db,
        first_recipe.title,
        first_recipe.description,
    )
    second_recipe_id = solution.add_recipe(
        empty_db,
        second_recipe.title,
        second_recipe.description,
    )

    first_ingredient_id = solution.add_ingredient(
        empty_db,
        first_recipe_id,
        first_ingredient.name,
        first_ingredient.quantity,
    )
    second_ingredient_id = solution.add_ingredient(
        empty_db,
        second_recipe_id,
        second_ingredient.name,
        second_ingredient.quantity,
    )

    return dto.TwoInsertedRecipesWithIngredients(
        first_recipe_id=first_recipe_id,
        second_recipe_id=second_recipe_id,
        first_recipe=first_recipe,
        second_recipe=second_recipe,
        first_ingredient_id=first_ingredient_id,
        second_ingredient_id=second_ingredient_id,
        first_ingredient=first_ingredient,
        second_ingredient=second_ingredient,
    )


@pytest.fixture
def search_recipes_data(
    recipe_factory: factories.RecipeDataFactory,
) -> dto.SearchRecipesData:
    first_matching_recipe = recipe_factory(
        title=f"Chicken {constants.SEARCH_WORD}",
    )
    second_matching_recipe = recipe_factory(
        title=f"Tomato {constants.SEARCH_WORD}",
    )
    first_non_matching_recipe = recipe_factory(
        title="Burger",
    )
    second_non_matching_recipe = recipe_factory(
        title="Fruit Salad",
    )

    return dto.SearchRecipesData(
        matching=[
            first_matching_recipe,
            second_matching_recipe,
        ],
        non_matching=[
            first_non_matching_recipe,
            second_non_matching_recipe,
        ],
        all=[
            first_matching_recipe,
            second_matching_recipe,
            first_non_matching_recipe,
            second_non_matching_recipe,
        ],
    )


@pytest.fixture
def inserted_search_recipes(
    empty_db: sqlite3.Cursor,
    search_recipes_data: dto.SearchRecipesData,
) -> dto.SearchRecipesData:
    for recipe in search_recipes_data.all:
        solution.add_recipe(
            empty_db,
            recipe.title,
            recipe.description,
        )

    return search_recipes_data
