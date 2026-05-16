from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RecipeSeed:
    title: str
    category: str
    cooking_time: int
    extra_meta: dict[str, Any]


@dataclass(frozen=True)
class RecipeDataset:
    recipes: tuple[RecipeSeed, ...]

    repeated_category: str
    quick_limit: int
    medium_limit: int

    common_meta_key: str
    unique_meta_key: str
    meta_key_for_update: str

    suspicious_title: str
    suspicious_title_part: str
    suspicious_category: str
    suspicious_meta_key: str


@dataclass(frozen=True)
class RecipeSearchDTO:
    title_part: str | None = None
    category: str | None = None
    minutes_from: int | None = None
    minutes_to: int | None = None
    required_meta_key: str | None = None
