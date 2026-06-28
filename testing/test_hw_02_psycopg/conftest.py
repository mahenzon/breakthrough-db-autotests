import json
from typing import TYPE_CHECKING
from typing import Any

import psycopg
import pytest
from faker import Faker

from testing.settings import settings
from testing.test_hw_02_psycopg import dto
from testing.test_hw_02_psycopg.db import create_recipe_tables
from testing.test_hw_02_psycopg.db import ensure_database_exists
from testing.test_hw_02_psycopg.db import make_admin_conninfo
from testing.test_hw_02_psycopg.db import make_conninfo_for_tests
from testing.test_hw_02_psycopg.db import reset_public_schema
from testing.test_hw_02_psycopg.db import validate_database_for_tests_name

how_to_pg = """\
No running Postgres found.
Run in with credentials 'postgres' for db, user, pass. Port 5432.
Or override values for test using env vars, example:
`export TEST_CONFIG__PG__PASSWORD=password`
For more check settings in source.
"""


if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture(scope="session")
def fake() -> Faker:
    Faker.seed(12345)
    return Faker()


@pytest.fixture(scope="session")
def database_for_tests_name() -> str:
    validate_database_for_tests_name(settings.pg.testing_db)
    return settings.pg.testing_db


@pytest.fixture(scope="session")
def admin_conninfo() -> str:
    return make_admin_conninfo(settings)


@pytest.fixture(scope="session")
def conninfo_for_tests() -> str:
    return make_conninfo_for_tests(settings)


@pytest.fixture(scope="session")
def admin_conn(admin_conninfo: str) -> Generator[psycopg.Connection]:
    try:
        with psycopg.connect(admin_conninfo, autocommit=True) as conn:
            yield conn
    except psycopg.OperationalError as exc:
        if exc.args and "connection failed" in exc.args[0]:
            pytest.fail(how_to_pg)
        else:
            raise


@pytest.fixture(scope="session")
def database_for_tests(
    admin_conn: psycopg.Connection,
    database_for_tests_name: str,
) -> str:
    ensure_database_exists(admin_conn, database_for_tests_name)
    return database_for_tests_name


@pytest.fixture
def conn(
    database_for_tests: str,  # noqa: ARG001
    conninfo_for_tests: str,
) -> Generator[psycopg.Connection]:
    with psycopg.connect(conninfo_for_tests) as connection:
        yield connection


@pytest.fixture
def empty_db(conn: psycopg.Connection) -> None:
    reset_public_schema(conn)
    create_recipe_tables(conn)
    conn.commit()


@pytest.fixture
def recipe_dataset(fake: Faker) -> dto.RecipeDataset:
    repeated_category = "Bakery"
    common_meta_key = "difficulty"
    unique_meta_key = "smoky"
    meta_key_for_update = "short-info"

    recipes = (
        dto.RecipeSeed(
            title=f"{fake.word().title()} Muffins",
            category=repeated_category,
            cooking_time=20,
            extra_meta={common_meta_key: "medium", "sweet": True},
        ),
        dto.RecipeSeed(
            title=f"{fake.word().title()} Bread",
            category=repeated_category,
            cooking_time=45,
            extra_meta={},
        ),
        dto.RecipeSeed(
            title=f"{fake.word().title()} Soup",
            category="Soup",
            cooking_time=90,
            extra_meta={common_meta_key: "hard", "warm": True},
        ),
        dto.RecipeSeed(
            title=f"{fake.word().title()} Salad",
            category="Salad",
            cooking_time=10,
            extra_meta={common_meta_key: "easy", "fresh": True},
        ),
        dto.RecipeSeed(
            title=f"{fake.word().title()} Noodles",
            category="Noodle",
            cooking_time=35,
            extra_meta={"noodles": True},
        ),
        dto.RecipeSeed(
            title=f"{fake.word().title()} Skewers",
            category="Grill",
            cooking_time=25,
            extra_meta={common_meta_key: "medium", unique_meta_key: True},
        ),
    )

    return dto.RecipeDataset(
        recipes=recipes,
        repeated_category=repeated_category,
        quick_limit=30,
        medium_limit=50,
        common_meta_key=common_meta_key,
        unique_meta_key=unique_meta_key,
        meta_key_for_update=meta_key_for_update,
        suspicious_title="Nice recipe'); drop table recipes; --",
        suspicious_title_part="x%' or true; drop table recipes; --",
        suspicious_category=f"{repeated_category}'; drop table recipes; --",
        suspicious_meta_key="bad-key'); drop table recipes; --",
    )


@pytest.fixture
def seeded_recipes(
    conn: psycopg.Connection,
    empty_db: None,  # noqa: ARG001
    recipe_dataset: dto.RecipeDataset,
) -> dto.RecipeDataset:
    for recipe in recipe_dataset.recipes:
        conn.execute(
            """
            insert into recipes (title, category, cooking_time, extra_meta)
            values (%s, %s, %s, %s::jsonb)
            """,
            (
                recipe.title,
                recipe.category,
                recipe.cooking_time,
                json.dumps(recipe.extra_meta),
            ),
        )

    conn.commit()
    return recipe_dataset


def expected_short_info(recipe: dto.RecipeSeed) -> str:
    return f"{recipe.category}:{recipe.cooking_time}"


def public_recipe_row(recipe: dto.RecipeSeed) -> dict[str, Any]:
    return {
        "title": recipe.title,
        "category": recipe.category,
        "cooking_time": recipe.cooking_time,
    }


def recipes_by_category(
    dataset: dto.RecipeDataset,
    category: str,
) -> list[dto.RecipeSeed]:
    return [recipe for recipe in dataset.recipes if recipe.category == category]


def recipes_with_max_time(
    recipes: tuple[dto.RecipeSeed, ...] | list[dto.RecipeSeed],
    max_minutes: int,
) -> list[dto.RecipeSeed]:
    return [recipe for recipe in recipes if recipe.cooking_time <= max_minutes]


def recipes_with_time_range(
    recipes: tuple[dto.RecipeSeed, ...] | list[dto.RecipeSeed],
    *,
    minutes_from: int | None = None,
    minutes_to: int | None = None,
) -> list[dto.RecipeSeed]:
    result = list(recipes)

    if minutes_from is not None:
        result = [recipe for recipe in result if recipe.cooking_time >= minutes_from]

    if minutes_to is not None:
        result = [recipe for recipe in result if recipe.cooking_time <= minutes_to]

    return result


def recipes_with_meta_key(
    recipes: tuple[dto.RecipeSeed, ...] | list[dto.RecipeSeed],
    key: str,
) -> list[dto.RecipeSeed]:
    return [recipe for recipe in recipes if key in recipe.extra_meta]


def assert_recipes_table_exists(conn: psycopg.Connection) -> None:
    table_exists = conn.execute("select to_regclass('public.recipes')").fetchone()[0]

    assert table_exists == "recipes"
