from __future__ import annotations

from typing import Any, overload

from _pytest.monkeypatch import MonkeyPatch, Notset

from .patchers import MethodOverloadPatcher

notset = Notset()


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
        value: Notset = notset,
        raising: bool = True,
    ) -> None: ...
    def setattr(
        self,
        target: str | object,
        name: object | str,
        value: object = notset,
        raising: bool = True,
    ) -> None: ...


class DelAttr(MonkeyPatch):  # type: ignore
    @overload
    def delattr(  # type: ignore
        self,
        target: Any,
        name: Notset = notset,
        raising: bool = True,
    ) -> None: ...
    def delattr(
        self,
        target: object | str,
        name: str | Notset = notset,
        raising: bool = True,
    ) -> None: ...
