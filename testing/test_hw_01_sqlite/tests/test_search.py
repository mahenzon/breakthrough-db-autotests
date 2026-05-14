from typing import TYPE_CHECKING

import pytest

from testing.test_hw_01_sqlite import constants
from testing.test_hw_01_sqlite import dto
from testing.test_hw_01_sqlite import factories as f

import solutions.hw_01_sqlite as solution

if TYPE_CHECKING:
    import sqlite3
    from collections.abc import Callable

    from faker import Faker


pytestmark = pytest.mark.sqlite


@pytest.mark.parametrize(
    "search_text",
    [
        constants.SEARCH_WORD,
        constants.SEARCH_WORD_LOWERCASE,
    ],
)
def test_search_recipes_finds_matching_titles_case_insensitive(
    empty_db: sqlite3.Cursor,
    inserted_search_recipes: dto.SearchRecipesData,
    search_text: str,
) -> None:
    rows = solution.search_recipes(
        empty_db,
        search_text,
    )

    expected_titles = sorted(
        [recipe.title for recipe in inserted_search_recipes.matching],
    )

    actual_titles = [row[constants.COL_TITLE] for row in rows]

    assert len(rows) == constants.EXPECTED_TWO_ROWS
    assert actual_titles == expected_titles


def test_search_recipes_returns_empty_list_if_no_matches(
    empty_db: sqlite3.Cursor,
    recipe_factory: f.RecipeDataFactory,
) -> None:
    recipes = [
        recipe_factory(),
        recipe_factory(),
    ]

    for recipe in recipes:
        solution.add_recipe(
            empty_db,
            recipe.title,
            recipe.description,
        )

    rows = solution.search_recipes(
        empty_db,
        constants.SEARCH_NO_MATCH,
    )

    assert rows == []


@pytest.mark.parametrize(
    "search_text_factory",
    [
        lambda recipe_title: recipe_title,
        lambda recipe_title: recipe_title[:3],
        lambda recipe_title: recipe_title.lower(),
    ],
)
def test_search_recipes_can_find_inserted_recipe_by_different_search_texts(
    empty_db: sqlite3.Cursor,
    recipe_factory: f.RecipeDataFactory,
    search_text_factory: Callable[[str], str],
    fake: Faker,
) -> None:
    recipe = recipe_factory(
        title=fake.sentence(nb_words=3).rstrip("."),
    )

    solution.add_recipe(
        empty_db,
        recipe.title,
        recipe.description,
    )

    search_text = search_text_factory(recipe.title)

    rows = solution.search_recipes(
        empty_db,
        search_text,
    )

    actual_titles = [row[constants.COL_TITLE] for row in rows]

    assert recipe.title in actual_titles
