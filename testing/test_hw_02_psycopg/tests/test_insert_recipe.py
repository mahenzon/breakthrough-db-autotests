from typing import TYPE_CHECKING

import pytest

from testing.test_hw_02_psycopg.conftest import assert_recipes_table_exists

import solutions.hw_02_psycopg as solution

if TYPE_CHECKING:
    import psycopg
    from faker import Faker
    from psycopg.rows import Row

    from testing.test_hw_02_psycopg import dto


pytestmark = [
    pytest.mark.usefixtures("empty_db"),
    pytest.mark.psycopg,
]


def fetch_recipe_by_id(
    conn: psycopg.Connection,
    recipe_id: int,
) -> Row:
    return conn.execute(
        """
        select title, category, cooking_time, extra_meta
        from recipes
        where id = %s
        """,
        (recipe_id,),
    ).fetchone()


def test_insert_recipe_returns_new_id_and_inserts_row(
    conn: psycopg.Connection,
    fake: Faker,
) -> None:
    title = fake.sentence(nb_words=3).rstrip(".")
    category = fake.random_element(
        elements=["Bakery", "Soup", "Salad", "Noodle", "Grill", "Dessert"],
    )
    cooking_time = fake.random_int(min=5, max=180)
    extra_meta = {
        "sweet": fake.boolean(),
        "difficulty": fake.random_element(elements=["easy", "medium", "hard"]),
        "source": fake.word(),
    }

    new_id = solution.insert_recipe_tstring(
        conn,
        title=title,
        category=category,
        cooking_time=cooking_time,
        extra_meta=extra_meta,
    )

    assert isinstance(new_id, int)

    row = fetch_recipe_by_id(conn, new_id)

    assert row is not None
    assert row[0] == title
    assert row[1] == category
    assert row[2] == cooking_time
    assert row[3] == extra_meta


def test_insert_recipe_stores_empty_json_when_extra_meta_is_none(
    conn: psycopg.Connection,
    fake: Faker,
) -> None:
    title = fake.sentence(nb_words=4).rstrip(".")
    category = fake.word().title()
    cooking_time = fake.random_int(min=1, max=300)

    new_id = solution.insert_recipe_tstring(
        conn,
        title=title,
        category=category,
        cooking_time=cooking_time,
        extra_meta=None,
    )

    row = fetch_recipe_by_id(conn, new_id)

    assert row is not None
    assert row[0] == title
    assert row[1] == category
    assert row[2] == cooking_time
    assert row[3] == {}


def test_insert_recipe_preserves_quotes_unicode_and_special_chars(
    conn: psycopg.Connection,
) -> None:
    title = 'Chef\'s "Special" item 🍽️'
    category = "Test/Category"
    cooking_time = 77
    extra_meta = {
        "note": "unicode text ✓",
        "emoji": "🔥",
        "quote": "It's good",
    }

    new_id = solution.insert_recipe_tstring(
        conn,
        title=title,
        category=category,
        cooking_time=cooking_time,
        extra_meta=extra_meta,
    )

    row = fetch_recipe_by_id(conn, new_id)

    assert row is not None
    assert row[0] == title
    assert row[1] == category
    assert row[2] == cooking_time
    assert row[3] == extra_meta


def test_insert_recipe_is_safe_with_sql_like_title(
    conn: psycopg.Connection,
    recipe_dataset: dto.RecipeDataset,
) -> None:
    new_id = solution.insert_recipe_tstring(
        conn,
        title=recipe_dataset.suspicious_title,
        category=recipe_dataset.repeated_category,
        cooking_time=recipe_dataset.quick_limit,
        extra_meta=None,
    )

    row = fetch_recipe_by_id(conn, new_id)

    assert row is not None
    assert row[0] == recipe_dataset.suspicious_title
    assert row[3] == {}

    assert_recipes_table_exists(conn)
