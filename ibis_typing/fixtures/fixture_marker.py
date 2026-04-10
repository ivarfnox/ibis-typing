import pytest
from attrs import frozen


@frozen
class FixtureMarker:
    """Automatically mark tests with specific fixtures with markers."""

    fixture_names: set[str]
    markers: list[pytest.MarkDecorator]

    @classmethod
    def for_fixtures(cls, *fixtures, markers: list[pytest.MarkDecorator]):
        return cls({fix.__name__ for fix in fixtures}, markers)

    def __call__(self, item: pytest.Item):
        fixtures = getattr(item, "fixturenames", ())

        if self.fixture_names & set(fixtures):
            for marker in self.markers:
                item.add_marker(marker)
