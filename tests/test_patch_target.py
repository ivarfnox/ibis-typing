from unittest import mock

from attrs import frozen

from ibis_typing import PatchTarget


def double(arg: float) -> float:
    return arg * 2


@frozen
class Multiplier:
    wrapped: float

    def multiply(self, other: float) -> float:
        return self.wrapped * other


def test_patch_target_function():
    target = PatchTarget.of(double)
    with mock.patch(str(target)) as mocked_target:
        # <exercise some code interacting with mocked_target>
        _ = mocked_target(5)

    assert mocked_target.mock_calls == [target(5)]


def test_patch_target_class():
    target = PatchTarget.of_instance(Multiplier)
    with mock.patch(str(target)) as mocked_target:
        # <exercise some code interacting with mocked_target>
        _ = mocked_target.multiply(5)

    assert mocked_target.multiply.mock_calls == [target.multiply(5)]
