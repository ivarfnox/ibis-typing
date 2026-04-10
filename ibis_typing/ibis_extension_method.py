"""Implements infix typed ibis table operators for more readable syntax.

Provides infix syntax for ibis_utils table functions:

- select
- aggregate
- left_join
- inner_join
- outer_join
- outer_parallel_join
"""

# pyright: reportRedeclaration=false, reportGeneralTypeIssues=false
from __future__ import annotations

import abc
from typing import TYPE_CHECKING, TypeVar, cast

from attrs import frozen
from ibis import Table, Value, ir

from ibis_typing.expression import GenericExpression, SingleInputTableExpression
from ibis_typing.extension_method import (
    DeferrableExtensionMethod,
    Deferred,
    ExtensionMethod,
)
from ibis_typing.ibis_adapter import IbisSchema, IbisTable

# Typed token for chaining instance methods after extension methods.
deferred = cast(Table, Deferred())


@frozen
class TableMethod(DeferrableExtensionMethod[Table, Table], abc.ABC):
    """Apply operation to Table on left-hand side of this operator."""

    @abc.abstractmethod
    def apply(self, table: Table) -> Table: ...

    def __rmatmul__(self, other):
        return self.apply(other)

    def as_expression_schema(
        self: TableMethod, origin: type[IbisSchema], /, preserves_schema: bool = False
    ) -> type[GenericExpression]:
        return TableMethodExpression(
            origin, self, preserves_schema
        ).as_expression_schema()


@frozen
class TableMethodExpression(SingleInputTableExpression):
    method: TableMethod
    preserves_schema: bool = False

    @property
    def output_schema(self):
        if not self.preserves_schema:
            return None
        return self.origin

    def __call__(self, origin: IbisTable) -> Table:
        return origin.table @ self.method


@frozen
class ValueMethod[T: Value, R: Value](DeferrableExtensionMethod[T, R], abc.ABC):
    """Apply operation to Value on left-hand side of this operator."""

    @abc.abstractmethod
    def apply(self, value: T) -> R: ...

    def __rmatmul__(self, other: T) -> R:
        return self.apply(other)


# Declare specializations for all column types to allow overriding type-checker behavior
# fmt: off
T = TypeVar("T", bound=Value)

class BooleanMethod(ValueMethod[T, ir.BooleanValue], abc.ABC): ...
class NumericMethod(ValueMethod[T, ir.NumericValue], abc.ABC): ...
class IntegerMethod(ValueMethod[T, ir.IntegerValue], abc.ABC): ...
class FloatingMethod(ValueMethod[T, ir.FloatingValue], abc.ABC): ...
class DecimalMethod(ValueMethod[T, ir.DecimalValue], abc.ABC): ...
class StringMethod(ValueMethod[T, ir.StringValue], abc.ABC): ...
class BinaryMethod(ValueMethod[T, ir.BinaryValue], abc.ABC): ...
class DateMethod(ValueMethod[T, ir.DateValue], abc.ABC): ...
class TimeMethod(ValueMethod[T, ir.TimeValue], abc.ABC): ...
class TimestampMethod(ValueMethod[T, ir.TimestampValue], abc.ABC): ...
class UUIDMethod(ValueMethod[T, ir.UUIDValue], abc.ABC): ...
class JSONMethod(ValueMethod[T, ir.JSONValue], abc.ABC): ...
class MapMethod(ValueMethod[T, ir.MapValue], abc.ABC): ...
class ArrayMethod(ValueMethod[T, ir.ArrayValue], abc.ABC): ...
class StructMethod(ValueMethod[T, ir.StructValue], abc.ABC): ...

if TYPE_CHECKING:
    # Note: IntelliJ does not handle separate .pyi files well.
    # Therefore, keep the type stub here after the actual implementation.
    @frozen
    class TableMethod(ExtensionMethod[Table, Table], Table):
        def apply(self, table: Table) -> Table: ...
        def __rmatmul__(self, other: Table) -> Table: ...
        def as_expression_schema(
                self, origin: type[IbisSchema], /, preserves_schema: bool = False
        ) -> type[GenericExpression]: ...

    @frozen
    class ValueMethod[T: Value, R: Value](ExtensionMethod[T, R]):
        def apply(self, value: T) -> R: ...
        def __rmatmul__(self, other: T) -> R: ...

    # Declare specializations for all column types to allow overriding type-checker behavior
    class BooleanMethod(ValueMethod[T, ir.BooleanValue], ir.BooleanValue): ...
    class NumericMethod(ValueMethod[T, ir.NumericValue], ir.NumericValue): ...
    class IntegerMethod(ValueMethod[T, ir.IntegerValue], ir.IntegerValue): ...
    class FloatingMethod(ValueMethod[T, ir.FloatingValue], ir.FloatingValue): ...
    class DecimalMethod(ValueMethod[T, ir.DecimalValue], ir.DecimalValue): ...
    class StringMethod(ValueMethod[T, ir.StringValue], ir.StringValue): ...
    class BinaryMethod(ValueMethod[T, ir.BinaryValue], ir.BinaryValue): ...
    class DateMethod(ValueMethod[T, ir.DateValue], ir.DateValue): ...
    class TimeMethod(ValueMethod[T, ir.TimeValue], ir.TimeValue): ...
    class TimestampMethod(ValueMethod[T, ir.TimestampValue], ir.TimestampValue): ...
    class UUIDMethod(ValueMethod[T, ir.UUIDValue], ir.UUIDValue): ...
    class JSONMethod(ValueMethod[T, ir.JSONValue], ir.JSONValue): ...
    class MapMethod(ValueMethod[T, ir.MapValue], ir.MapValue): ...
    class ArrayMethod(ValueMethod[T, ir.ArrayValue], ir.ArrayValue): ...
    class StructMethod(ValueMethod[T, ir.StructValue], ir.StructValue): ...
