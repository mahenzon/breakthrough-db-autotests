from typing import TYPE_CHECKING

from testing.test_hw_01_sqlite import constants
from testing.test_hw_01_sqlite import dto

if TYPE_CHECKING:
    from faker import Faker


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
