from __future__ import annotations

import abc

import ibis
from attrs import frozen

from . import ibis_types as it
from .expression import GenericExpression, SingleInputTableExpression
from .ibis_adapter import IbisSchema, IbisTable

_ = it  # Needed for doctests


@frozen
class RevertibleTableExpression[S: IbisSchema](SingleInputTableExpression[S], abc.ABC):
    """Expressions which can be reverted and chained.

    >>> from ibis_typing import dt, IbisSchema, this

    >>> @frozen
    ... class IntSchema(IbisSchema):
    ...     value: it.Int64 = None

    >>> @frozen
    ... class FloatRevertible(RevertibleTableExpression):
    ...     col: it.NameOrType
    ...
    ...     def __call__(self, origin: IbisTable):
    ...         return origin.table.cast({self.col: dt.Float64})
    ...
    ...     def revert_call(self, table: IbisTable):
    ...         return table.table.cast({self.col: self.origin.table_schema[self.col]})

    >>> @frozen
    ... class StringRevertible(RevertibleTableExpression):
    ...     col: it.NameOrType
    ...
    ...     def __call__(self, origin: IbisTable):
    ...         return origin.table.cast({self.col: dt.String})
    ...
    ...     def revert_call(self, table: IbisTable):
    ...         return table.table.cast({self.col: self.origin.table_schema[self.col]})

    >>> int_table = IntSchema.of_rows([])
    >>> float_table = (
    ...     FloatRevertible(IntSchema, "value")
    ...     .as_expression_schema()
    ...     .from_expression(int_table)
    ... )
    >>> str_table = (
    ...     StringRevertible(float_table.table_schema, "value")
    ...     .as_expression_schema()
    ...     .from_expression(float_table)
    ... )
    >>> reverted_table = revert_all(str_table)

    >>> int_table.table_schema == IntSchema
    True
    >>> reverted_table.table_schema == IntSchema
    True
    """

    def revert_expression(self, transformed: IbisTable) -> IbisTable[S]:
        table = self.revert_call(transformed)
        return self.origin.of(table)

    @abc.abstractmethod
    def __call__(self, origin: IbisTable[S]) -> ibis.Table: ...

    @abc.abstractmethod
    def revert_call(self, transformed: IbisTable) -> ibis.Table: ...


def revert_all(table: IbisTable) -> IbisTable:
    """Revert all revertible expressions in the chain."""
    while issubclass((schema := table.table_schema), GenericExpression) and isinstance(
        constructor := schema.get_table_expression(), RevertibleTableExpression
    ):
        table = constructor.revert_expression(table)

    return table
