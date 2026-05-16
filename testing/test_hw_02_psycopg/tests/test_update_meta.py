"""
JSONB update tests.

`update_recipe_meta_tstring(meta_key)` should add:

    meta_key: category || ':' || cooking_time::text

Only rows where the key is missing should be updated.
"""

from typing import TYPE_CHECKING

import pytest

from testing.test_hw_02_psycopg.conftest import assert_recipes_table_exists
from testing.test_hw_02_psycopg.conftest import expected_short_info

import solutions.hw_02_psycopg as solution

if TYPE_CHECKING:
    import psycopg
    from faker import Faker

    from testing.test_hw_02_psycopg import dto


pytestmark = pytest.mark.psycopg


def test_update_recipe_meta_adds_jsonb_key(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    updated_count = solution.update_recipe_meta_tstring(
        conn,
        seeded_recipes.meta_key_for_update,
    )

    assert updated_count == len(seeded_recipes.recipes)


def test_update_recipe_meta_adds_expected_values(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    solution.update_recipe_meta_tstring(
        conn,
        seeded_recipes.meta_key_for_update,
    )

    rows = conn.execute("""
        select title, extra_meta
        from recipes
        """).fetchall()

    expected_by_title = {
        recipe.title: expected_short_info(recipe) for recipe in seeded_recipes.recipes
    }

    actual_by_title = {
        title: extra_meta[seeded_recipes.meta_key_for_update]
        for title, extra_meta in rows
    }

    assert actual_by_title == expected_by_title


def test_update_recipe_meta_does_not_overwrite_existing_key(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
    fake: Faker,
) -> None:
    existing_recipe = seeded_recipes.recipes[0]
    custom_value = fake.sentence(nb_words=3).rstrip(".")

    conn.execute(
        """
        update recipes
        set extra_meta = extra_meta || jsonb_build_object(%s::text, %s::text)
        where title = %s
        """,
        (
            seeded_recipes.meta_key_for_update,
            custom_value,
            existing_recipe.title,
        ),
    )
    conn.commit()

    updated_count = solution.update_recipe_meta_tstring(
        conn,
        seeded_recipes.meta_key_for_update,
    )

    assert updated_count == len(seeded_recipes.recipes) - 1

    value = conn.execute(
        """
        select extra_meta ->> %s
        from recipes
        where title = %s
        """,
        (
            seeded_recipes.meta_key_for_update,
            existing_recipe.title,
        ),
    ).fetchone()[0]

    assert value == custom_value


def test_update_recipe_meta_updates_only_missing_keys_on_second_run(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    first_count = solution.update_recipe_meta_tstring(
        conn,
        seeded_recipes.meta_key_for_update,
    )
    second_count = solution.update_recipe_meta_tstring(
        conn,
        seeded_recipes.meta_key_for_update,
    )

    assert first_count == len(seeded_recipes.recipes)
    assert second_count == 0


def test_update_recipe_meta_accepts_key_with_dash(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
    fake: Faker,
) -> None:
    meta_key = f"{fake.word()}-{fake.word()}"

    updated_count = solution.update_recipe_meta_tstring(conn, meta_key)

    assert updated_count == len(seeded_recipes.recipes)

    expected_recipe = seeded_recipes.recipes[0]

    value = conn.execute(
        """
        select extra_meta ->> %s
        from recipes
        where title = %s
        """,
        (meta_key, expected_recipe.title),
    ).fetchone()[0]

    assert value == expected_short_info(expected_recipe)


def test_update_recipe_meta_is_safe_with_sql_like_key(
    conn: psycopg.Connection,
    seeded_recipes: dto.RecipeDataset,
) -> None:
    updated_count = solution.update_recipe_meta_tstring(
        conn,
        seeded_recipes.suspicious_meta_key,
    )

    assert updated_count == len(seeded_recipes.recipes)

    expected_recipe = seeded_recipes.recipes[0]

    value = conn.execute(
        """
        select extra_meta ->> %s
        from recipes
        where title = %s
        """,
        (seeded_recipes.suspicious_meta_key, expected_recipe.title),
    ).fetchone()[0]

    assert value == expected_short_info(expected_recipe)
    assert_recipes_table_exists(conn)
