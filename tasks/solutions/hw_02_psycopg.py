from typing import TYPE_CHECKING
from typing import Any
from typing import Protocol

if TYPE_CHECKING:
    import psycopg


class RecipeSearch(Protocol):
    title_part: str | None = None
    category: str | None = None
    minutes_from: int | None = None
    minutes_to: int | None = None
    required_meta_key: str | None = None


def insert_recipe_tstring(
    conn: psycopg.Connection,
    title: str,
    category: str,
    cooking_time: int,
    extra_meta: dict[str, Any] | None = None,
) -> int:
    """
    Вставить новый рецепт в таблицу `recipes`.

    Таблица:

        recipes (
            id serial primary key,
            title text not null,
            category text not null,
            cooking_time integer not null,
            extra_meta jsonb not null,
            created_at timestamp not null
        )

    Требования:
    - Используйте t-строки для SQL.
    - Вставить нужно поля `title`, `category`, `cooking_time`, `extra_meta`.
    - Если в `extra_meta` пришло None, сохранить в таблицу надо пустой JSON объект.
    - Верните id созданной записи.
    """
    raise NotImplementedError


def filter_quick_recipes(
    conn: psycopg.Connection,
    category: str,
    max_minutes: int,
) -> list[dict[str, Any]]:
    """
    Вернуть рецепты одной категории, где время готовки не превышает `max_minutes`.

    Требования:
    - Используйте t-строки для SQL.
    - Запрашивайте только эти колонки:
        id, title, category, cooking_time
    - Результат - список из словарей.
    - Отсортируйте по cooking_time ascending, id ascending.
    """
    raise NotImplementedError


def select_dynamic_recipe_column(
    conn: psycopg.Connection,
    column_name: str,
    order_by_field: str = "id",
) -> list[dict[str, Any]]:
    """
    Запросите из таблицы `recipes` колонку `title` и одну дополнительную колонку,
    переданную динамически. Отсортируйте по указанному полю (отдельно от доп. колонки).

    Например:

        select_dynamic_recipe_column(conn, "category")

    должно получиться примерно такое:

        select title, category
        from recipes
        order by id

    Требования:
    - Используйте t-строки для SQL.
    - Результат - список из словарей.
    """
    raise NotImplementedError


def update_recipe_meta_tstring(
    conn: psycopg.Connection,
    meta_key: str,
) -> int:
    """
    Обновите JSONB колонку `extra_meta` рецептов,
    добавьте новое поле (если ещё нет):
    - ключ передан в meta_key
    - значение - склеенные через двоеточие категория и время готовки.

    Обновите каждый рецепт без meta_key поля, схематично так:

        meta_key: category || ':' || cooking_time::text

    Требования:
    - Используйте t-строки для SQL.
    - Не перезаписывайте meta_key, если значение по такому ключу уже есть (не null).
    - Верните количество обновленных строк.
    """
    raise NotImplementedError


def search_recipes_tstring(
    conn: psycopg.Connection,
    search: RecipeSearch,
) -> list[Any]:
    """
    Реализуйте поиск по рецептам.

    Все параметры для поиска переданы в объекте search.
    Используйте атрибуты объекта search для поиска.
    Все атрибуты опциональны:
    если там None, то фильтрация не требуется.

    Правила фильтрации:
    - `title_part`:
        любое вхождение в title, независимо от регистра

    - `category`:
        полное совпадение категории

    - `minutes_from`:
        cooking_time >= minutes_from

    - `minutes_to`:
        cooking_time <= minutes_to

    - `required_meta_key`:
        В поле extra_meta есть ключ required_meta_key

    Требования:
    - Используйте t-строки для SQL.
    - Собирайте кусочки для фильтрации в list.
    - Объедините правила фильтрации через `sql.SQL(" AND ").join(...)`.
    - Используйте подходящие модификаторы при построении запроса.
    - Запросите все доступные колонки.
    - Отсортируйте по id ascending.
    - Верните список из строк namedtuple, чтобы можно было обращаться по атрибутам.
    """
    raise NotImplementedError
