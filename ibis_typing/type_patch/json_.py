from __future__ import annotations

from typing import TYPE_CHECKING, overload

from ibis import ir
from ibis.expr.types.json import JSONValue

from . import inspect_types
from .patchers import (
    MethodOverloadPatcher,
    MethodSelfReturnTypePatcher,
    TypeCheckingModulePatcher,
    TypingOverloadImportPatcher,
)


def get_patchers():
    methods = [
        JSONValueMap,
        JSONValueArray,
    ]
    self_methods = inspect_types.get_methods(JSONValue, JSONValue)
    return [
        TypeCheckingModulePatcher(__file__),
        TypingOverloadImportPatcher(),
        *(MethodSelfReturnTypePatcher(method) for method in self_methods),
        *(MethodOverloadPatcher(patch) for patch in methods),
    ]


# Note: Overloading decorated functions moves the decorator to the top of the patch...
class JSONValueMap(JSONValue):
    @overload
    def map(self) -> ir.MapValue[ir.StringValue, ir.JSONValue]: ...
    @property
    @overload
    def map(self) -> ir.MapValue[ir.StringValue, ir.JSONValue]: ...
    @property
    def map(self) -> ir.MapValue:
        raise NotImplementedError


class JSONValueArray(JSONValue):
    @overload
    def array(self) -> ir.ArrayValue[Self]: ...
    @property
    @overload
    def array(self) -> ir.ArrayValue[Self]: ...
    @property
    def array(self) -> ir.ArrayValue:
        raise NotImplementedError


if TYPE_CHECKING:
    from typing import Self
