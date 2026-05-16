import pytest  # noqa: TC002


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
    config.addinivalue_line(
        "markers",
        "psycopg: tests for PostgreSQL / psycopg homework tasks",
    )
