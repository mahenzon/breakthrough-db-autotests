from dataclasses import dataclass

from testing.test_hw_01_sqlite import constants


@dataclass(frozen=True)
class RecipeData:
    title: str
    description: str = constants.EMPTY_STRING


@dataclass(frozen=True)
class IngredientData:
    name: str
    quantity: str = constants.EMPTY_STRING


@dataclass(frozen=True)
class RecipeWithIngredientsData:
    recipe: RecipeData
    ingredients: list[IngredientData]


@dataclass(frozen=True)
class InsertedRecipe:
    id: int
    data: RecipeData


@dataclass(frozen=True)
class InsertedRecipeWithIngredients:
    recipe_id: int
    ingredient_ids: list[int]
    data: RecipeWithIngredientsData


@dataclass(frozen=True)
class TwoInsertedRecipesWithIngredients:
    first_recipe_id: int
    second_recipe_id: int
    first_recipe: RecipeData
    second_recipe: RecipeData
    first_ingredient_id: int
    second_ingredient_id: int
    first_ingredient: IngredientData
    second_ingredient: IngredientData


@dataclass(frozen=True)
class SearchRecipesData:
    matching: list[RecipeData]
    non_matching: list[RecipeData]
    all: list[RecipeData]


TwoInsertedRecipesWIngredients = TwoInsertedRecipesWithIngredients
