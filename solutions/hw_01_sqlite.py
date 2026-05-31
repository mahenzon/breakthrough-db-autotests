"""
Структура БД:

1. Таблица recipes

    id INTEGER PRIMARY KEY AUTOINCREMENT
    title TEXT NOT NULL UNIQUE
    description TEXT NOT NULL DEFAULT ''

2. Таблица ingredients

    id INTEGER PRIMARY KEY AUTOINCREMENT
    recipe_id INTEGER NOT NULL
    name TEXT NOT NULL
    quantity TEXT NOT NULL DEFAULT ''


Ингредиенты должны быть связаны с рецептами через recipe_id.

При удалении рецепта его ингредиенты тоже должны быть удалены.
"""

import sqlite3


def create_tables(
    cur: sqlite3.Cursor,
    *,
    drop: bool = False,
) -> None:
    """
    Создать таблицы, если ещё не существуют.

    1. recipes

        Columns:
            id:
                INTEGER PRIMARY KEY AUTOINCREMENT

            title:
                TEXT
                Required
                Unique

            description:
                TEXT
                Required
                Default value: empty string

    2. ingredients

        Columns:
            id:
                INTEGER PRIMARY KEY AUTOINCREMENT

            recipe_id:
                INTEGER
                Required
                References recipes(id)

            name:
                TEXT
                Required

            quantity:
                TEXT
                Required
                Default value: empty string

    Args:
        cur:
            SQLite cursor.

        drop:
            If True, delete existing tables first.
    """
    if drop:
        cur.execute("DROP TABLE IF EXISTS ingredients")
        cur.execute("DROP TABLE IF EXISTS recipes")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        description TEXT NOT NULL DEFAULT ''
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        quantity TEXT NOT NULL DEFAULT '',
        CONSTRAINT fk_ingredients_recipe_id
            FOREIGN KEY (recipe_id)
            REFERENCES recipes (id)
            ON DELETE CASCADE
    )
    """)


def add_recipe(
    cur: sqlite3.Cursor,
    title: str,
    description: str = "",
) -> int:
    """
    Добавить новый рецепт в таблицу рецептов.

    Использовать параметры запроса.
    Вернуть ID созданного рецепта.

    Args:
        cur:
            SQLite cursor.

        title:
            Recipe title.

        description:
            Recipe description.
            Default value should be an empty string.

    Returns:
        The id of the newly inserted recipe.

    Example:
        recipe_id = add_recipe(
            cur,
            "Pasta",
            "Cheesy pasta",
        )
    """
    parameters = (
        title,
        description,
    )
    res = cur.execute(
        """
    INSERT INTO recipes (title, description)
        VALUES (?, ?)
        RETURNING id
    """,
        parameters,
    )
    recipe_id: int = res.fetchone()["id"]

    cur.connection.commit()

    return recipe_id


def add_ingredient(
    cur: sqlite3.Cursor,
    recipe_id: int,
    name: str,
    quantity: str = "",
) -> int:
    """
    Добавить новый ингредиент в таблицу ингредиентов.

    Использовать параметры запроса.
    Вернуть ID созданного ингредиента.

    Args:
        cur:
            SQLite cursor.

        recipe_id:
            Id of the recipe this ingredient belongs to.

        name:
            Ingredient name.

        quantity:
            Ingredient quantity.
            Default value should be an empty string.

    Returns:
        The id of the newly inserted ingredient.

    Example:
        ingredient_id = add_ingredient(
            cur,
            recipe_id,
            "Cheese",
            "100g",
        )
    """
    res = cur.execute(
        """
        INSERT INTO ingredients (recipe_id, name, quantity)
            VALUES (?, ?, ?)
            RETURNING id
        """,
        (
            recipe_id,
            name,
            quantity,
        ),
    )

    ingredient_id: int = res.fetchone()["id"]
    cur.connection.commit()
    return ingredient_id


def get_recipe_by_title(
    cur: sqlite3.Cursor,
    title: str,
) -> sqlite3.Row | None:
    """
    Вернуть один рецепт по названию.

    Вернуть None, если не найдено.

    Использовать параметры запроса.

    Args:
        cur:
            SQLite cursor.

        title:
            Recipe title to search for.

    Returns:
        sqlite3.Row if the recipe exists.
        None if the recipe does not exist.

    Returned row must contain:
        - id
        - title
        - description

    Example:
        recipe = get_recipe_by_title(cur, "Pasta")

        if recipe is not None:
            print(recipe["title"])
    """
    res = cur.execute(
        """
        SELECT id, title, description
        FROM recipes
        WHERE title = ?
        """,
        (title,),
    )

    row = res.fetchone()
    if not row:
        return None

    return row


def get_ingredients_for_recipe(
    cur: sqlite3.Cursor,
    recipe_id: int,
) -> list[sqlite3.Row]:
    """
    Вернуть все ингредиенты для рецепта.

    Отсортировать по ID.

    Использовать параметры запроса.

    Вернуть пустой список, если ничего не найдено.

    Args:
        cur:
            SQLite cursor.

        recipe_id:
            Id of the recipe.

    Returns:
        A list of sqlite3.Row objects.

    Each row must contain:
        - id
        - recipe_id
        - name
        - quantity

    Example:
        ingredients = get_ingredients_for_recipe(cur, recipe_id)

        for ingredient in ingredients:
            print(ingredient["name"])
    """
    res = cur.execute(
        """
    SELECT id, recipe_id, name, quantity
    FROM ingredients
        WHERE recipe_id = ?
        ORDER BY recipe_id ASC
    """,
        (recipe_id,),
    )
    return res.fetchall()


def update_recipe_description(
    cur: sqlite3.Cursor,
    title: str,
    description: str,
) -> int:
    """
    Обновить описание рецепта по названию.

    Использовать параметры запроса.

    Вернуть количество обновленных строк.

    Args:
        cur:
            SQLite cursor.

        title:
            Title of the recipe to update.

        description:
            New recipe description.

    Returns:
        Number of updated rows.

    Example:
        updated_count = update_recipe_description(
            cur,
            "Chicken Soup",
            "Soup with chicken and noodles",
        )
    """
    res = cur.execute(
        """
        UPDATE recipes
        SET description = ?
            WHERE title = ?
        """,
        (
            description,
            title,
        ),
    )
    return res.rowcount


def delete_recipe(
    cur: sqlite3.Cursor,
    title: str,
) -> int:
    """
    Удалить рецепт по названию.

    Использовать параметры запроса.

    Все ингредиенты рецепта должны быть удалены.

    Вернуть количество удаленных строк.

    Args:
        cur:
            SQLite cursor.

        title:
            Title of the recipe to delete.

    Returns:
        Number of deleted recipe rows.

    Example:
        deleted_count = delete_recipe(cur, "Pancakes")
    """

    res = cur.execute(
        """
        DELETE FROM recipes
            where title = ?
        """,
        (title,),
    )
    return res.rowcount


def search_recipes(
    cur: sqlite3.Cursor,
    text: str,
) -> list[sqlite3.Row]:
    """
    Найти рецепты по совпадению названия.

    Использовать параметры запроса.

    Args:
        cur:
            SQLite cursor.

        text:
            Text to search for inside recipe titles.

    Returns:
        A list of sqlite3.Row objects.

    Each row must contain:
        - id
        - title
        - description

    Example:
        rows = search_recipes(cur, "soup")

        # Should find titles like:
        # - Chicken Soup
        # - Tomato Soup
    """

    text_for_search = "%" + text + "%"

    res = cur.execute(
        """
        SELECT id, title, description
        FROM recipes
            WHERE lower(title) like lower(?)
            ORDER BY title ASC
        """,
        (text_for_search,),
    )
    return res.fetchall()
