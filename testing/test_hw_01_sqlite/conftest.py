import sqlite3
from typing import TYPE_CHECKING

import pytest
from faker import Faker

from testing.test_hw_01_sqlite import constants
from testing.test_hw_01_sqlite import dto

import solutions.hw_01_sqlite as solution

if TYPE_CHECKING:
    from collections.abc import Generator

pytestmark = pytest.mark.sqlite


@pytest.fixture(scope="session")
def fake() -> Faker:
    return Faker()


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


class RecipeDataFactory:
    def __init__(self, fake: Faker) -> None:
        self.fake = fake

    def __call__(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> dto.RecipeData:
        return dto.RecipeData(
            title=title or self.fake.unique.sentence(nb_words=3).rstrip("."),
            description=(
                description
                if description is not None
                else self.fake.sentence()
            ),
        )


class RecipeWithoutDescriptionFactory:
    def __init__(self, fake: Faker) -> None:
        self.fake = fake

    def __call__(
        self,
        *,
        title: str | None = None,
    ) -> dto.RecipeData:
        return dto.RecipeData(
            title=title or self.fake.unique.sentence(nb_words=3).rstrip("."),
            description=constants.EMPTY_STRING,
        )


class IngredientDataFactory:
    def __init__(self, fake: Faker) -> None:
        self.fake = fake

    def __call__(
        self,
        *,
        name: str | None = None,
        quantity: str | None = None,
    ) -> dto.IngredientData:
        return dto.IngredientData(
            name=name or self.fake.unique.word().title(),
            quantity=(
                quantity
                if quantity is not None
                else self.fake.random_element(
                    elements=(
                        "100g",
                        "200g",
                        "1 tsp",
                        "500ml",
                        "2 pieces",
                    ),
                )
            ),
        )


class IngredientWithoutQuantityFactory:
    def __init__(self, fake: Faker) -> None:
        self.fake = fake

    def __call__(
        self,
        *,
        name: str | None = None,
    ) -> dto.IngredientData:
        return dto.IngredientData(
            name=name or self.fake.unique.word().title(),
            quantity=constants.EMPTY_STRING,
        )


class RecipeWithIngredientsFactory:
    def __init__(
        self,
        recipe_factory: RecipeDataFactory,
        ingredient_factory: IngredientDataFactory,
    ) -> None:
        self.recipe_factory = recipe_factory
        self.ingredient_factory = ingredient_factory

    def __call__(
        self,
        *,
        ingredient_count: int = constants.EXPECTED_THREE_ROWS,
    ) -> dto.RecipeWithIngredientsData:
        return dto.RecipeWithIngredientsData(
            recipe=self.recipe_factory(),
            ingredients=[
                self.ingredient_factory() for _ in range(ingredient_count)
            ],
        )


@pytest.fixture
def recipe_factory(fake: Faker) -> RecipeDataFactory:
    return RecipeDataFactory(fake)


@pytest.fixture
def recipe_without_description_factory(
    fake: Faker,
) -> RecipeWithoutDescriptionFactory:
    return RecipeWithoutDescriptionFactory(fake)


@pytest.fixture
def ingredient_factory(fake: Faker) -> IngredientDataFactory:
    return IngredientDataFactory(fake)


@pytest.fixture
def ingredient_without_quantity_factory(
    fake: Faker,
) -> IngredientWithoutQuantityFactory:
    return IngredientWithoutQuantityFactory(fake)


@pytest.fixture
def recipe_with_ingredients_factory(
    recipe_factory: RecipeDataFactory,
    ingredient_factory: IngredientDataFactory,
) -> RecipeWithIngredientsFactory:
    return RecipeWithIngredientsFactory(
        recipe_factory=recipe_factory,
        ingredient_factory=ingredient_factory,
    )


@pytest.fixture
def inserted_recipe(
    empty_db: sqlite3.Cursor,
    recipe_factory: RecipeDataFactory,
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
    recipe_without_description_factory: RecipeWithoutDescriptionFactory,
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
    recipe_with_ingredients_factory: RecipeWithIngredientsFactory,
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
    recipe_factory: RecipeDataFactory,
    ingredient_factory: IngredientDataFactory,
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
    recipe_factory: RecipeDataFactory,
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
