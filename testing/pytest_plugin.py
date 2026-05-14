import os
from importlib.resources import files
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pytest


def _has_option(
    args: Sequence[str],
    option_name: str,
) -> bool:
    """
    Return True for both:
        --cov
        --cov=solutions
    """
    return any(arg == option_name or arg.startswith(f"{option_name}=") for arg in args)


def _coverage_config_path() -> str:
    return str(files("testing").joinpath("coverage.ini"))


def pytest_load_initial_conftests(
    early_config: pytest.Config,  # noqa: ARG001
    args: list[str],
    parser: pytest.Parser,  # noqa: ARG001
) -> None:
    """
    Configure pytest-cov automatically for student runs.

    This runs early enough to add CLI args before pytest parses them.
    """
    if os.getenv("PY_DB_AUTOTESTS_DISABLE_COV") == "1":
        return

    if not _has_option(args, "--cov"):
        args.append("--cov=solutions")

    if not _has_option(args, "--cov-config"):
        args.append(f"--cov-config={_coverage_config_path()}")

    if not _has_option(args, "--cov-report"):
        args.append("--cov-report=term-missing")
        args.append("--cov-report=html")


def pytest_configure(
    config: pytest.Config,
) -> None:
    """
    Register custom markers to avoid PytestUnknownMarkWarning.
    """
    config.addinivalue_line(
        "markers",
        "sqlite: tests for SQLite homework tasks",
    )
