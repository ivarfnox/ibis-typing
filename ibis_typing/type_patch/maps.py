from __future__ import annotations

from typing import TypeAliasType, cast, overload

from ibis import ir
from ibis.expr.types.maps import MapColumn, MapValue

from .patchers import (
    MethodOverloadPatcher,
    TypingOverloadImportPatcher,
    ValueTypeParameterPatcher,
)

type K = ir.Value
type V = ir.Value
_kv = cast(list[TypeAliasType], [K, V])


def get_patchers():
    methods = [
        MapColumnGetItem,
        MapValueGetItem,
        MapValueKeys,
        MapValueValues,
    ]
    return [
        TypingOverloadImportPatcher(),
        *(MethodOverloadPatcher(patch) for patch in methods),
        ValueTypeParameterPatcher(MapValue, _kv),
        ValueTypeParameterPatcher(MapColumn, _kv, base=MapValue),
    ]


class MapValueGetItem(MapValue):
    @overload
    def __getitem__(self, key: ir.Value) -> V: ...  # type: ignore

    def __getitem__(self, key: ir.Value) -> ir.Value:
        raise NotImplementedError


class MapColumnGetItem(MapColumn):
    @overload
    def __getitem__(self, key: ir.Value) -> V | ir.Column: ...  # type: ignore

    def __getitem__(self, key: ir.Value) -> ir.Column:
        raise NotImplementedError


class MapValueKeys(MapValue):
    @overload
    def keys(self) -> ir.ArrayValue[K]: ...  # type: ignore

    def keys(self) -> ir.ArrayValue:
        raise NotImplementedError


class MapValueValues(MapValue):
    @overload
    def values(self) -> ir.ArrayValue[V]: ...  # type: ignore

    def values(self) -> ir.ArrayValue:
        raise NotImplementedError
