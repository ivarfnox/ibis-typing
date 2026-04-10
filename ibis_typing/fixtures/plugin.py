import pytest

pytest_plugins = [
    "ibis_typing.fixtures.duck_connection",
    "ibis_typing.fixtures.expressions",
    "ibis_typing.fixtures.ibis_connection",
    "ibis_typing.fixtures.ibis_time",
    "ibis_typing.fixtures.trino_connection",
]

pytest.register_assert_rewrite(*pytest_plugins)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Add markers like ``@pytest.mark.trino`` to tests."""
    from . import duck_connection, marks, trino_connection
    from .fixture_marker import FixtureMarker

    auto_markers = [
        FixtureMarker.for_fixtures(
            duck_connection.duck_connection,
            markers=[marks.ibis, marks.duck],
        ),
        FixtureMarker.for_fixtures(
            trino_connection.trino_connection,
            markers=[marks.ibis, marks.trino],
        ),
    ]

    for item in items:
        for marker in auto_markers:
            marker(item)
