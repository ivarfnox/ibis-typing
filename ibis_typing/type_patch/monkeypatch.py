from __future__ import annotations

from typing import Any, overload

from _pytest.compat import NOTSET, NotSetType
from _pytest.monkeypatch import MonkeyPatch

from .patchers import MethodOverloadPatcher


def get_patchers():
    methods = [
        SetAttr,
        DelAttr,
    ]
    return [
        *[MethodOverloadPatcher(patch) for patch in methods],
    ]


class SetAttr(MonkeyPatch):  # type: ignore
    @overload
    def setattr(  # type: ignore
        self,
        target: Any,
        name: object,
        value: NotSetType = NOTSET,
        raising: bool = True,
    ) -> None: ...
    def setattr(
        self,
        target: str | object,
        name: object | str,
        value: object = NOTSET,
        raising: bool = True,
    ) -> None: ...


class DelAttr(MonkeyPatch):  # type: ignore
    @overload
    def delattr(  # type: ignore
        self,
        target: Any,
        name: NotSetType = NOTSET,
        raising: bool = True,
    ) -> None: ...
    def delattr(
        self,
        target: object | str,
        name: str | NotSetType = NOTSET,
        raising: bool = True,
    ) -> None: ...
