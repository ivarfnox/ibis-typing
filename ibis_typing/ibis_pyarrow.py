"""Implements IbisTable -> list[IbisSchema] interface.

Implement reading Python IbisSchema instances from an IbisTable expression.
Provides a type compatibility layer between Python, Ibis, and PyArrow.
"""

from __future__ import annotations

import functools
import json
import logging
import uuid
from collections.abc import Iterable, Sequence
from typing import TYPE_CHECKING, Any
from typing import cast as typing_cast

import attrs
import ibis
import pyarrow as pa
from attrs import frozen
from ibis import ir
from ibis.expr import datatypes as dt
from ibis.expr import operations

from . import ibis_ops, utils
from .custom.op_cast import op_cast
from .ibis_ops import JsonFormat, JsonParse

STRUCT_NOT_SUPPORTED = "Struct values are not supported. Convert to supported types."


if TYPE_CHECKING:
    from . import IbisSchema, IbisTable

logger = logging.getLogger(__name__)


def fetch_expr[T](
    expr: ibis.Expr,
    /,
    connection: ibis.BaseBackend | None = None,
    *,
    type_: type[T] | None = None,
) -> T:
    backend = connection or expr._find_backend(use_default=True)
    ret = backend.to_pyarrow(expr)
    ret: pa.Scalar | pa.ChunkedArray | pa.Table
    match ret:
        case pa.Scalar():
            return ret.as_py()
        case pa.ChunkedArray() | pa.Table():
            return ret.to_pylist()
        case _:
            raise TypeError(f"Unexpected pyarrow type: {type(ret)}")


def fetch_table[T: IbisSchema](
    ibis_table: IbisTable[T],
    /,
    connection: ibis.BaseBackend | None = None,
) -> Iterable[T]:
    backend = connection or ibis_table.table._find_backend(use_default=True)
    converter = PyArrowConverter(ibis_table.table_schema)

    converted = converter.ibis_to_pyarrow(ibis_table.table)
    batches = backend.to_pyarrow_batches(converted, chunk_size=1_000)
    for batch in batches:
        logger.debug("Fetching batch from query result.")
        rows = zip(*batch.to_pydict().values())
        yield from (converter.pyarrow_to_py(row) for row in rows)


def as_literal_table(
    rows: Sequence[IbisSchema], *, name: str | None = None
) -> ibis.Table:
    assert rows
    cls = type(rows[0])
    name = name or f"{cls.__name__}__{utils.short_hash(rows)}"

    converter = PyArrowConverter(cls)

    pyarrows = [converter.py_to_pyarrow(row) for row in rows]
    schema = converter.ibis_to_pyarrow(ibis.table(cls.table_schema)).schema()

    table = ibis_ops.literal_table(name, pyarrows, schema)

    return converter.pyarrow_to_ibis(table)


@frozen
class PyArrowConverter[T: IbisSchema]:
    schema: type[T]

    def py_to_pyarrow(self, value: T) -> tuple:
        values = attrs.astuple(value)
        return tuple(py_to_pyarrow(val, t) for val, t in zip(values, self.ibis_types()))

    def pyarrow_to_py(self, row: tuple) -> T:
        values = (pyarrow_to_py(val, t) for val, t in zip(row, self.ibis_types()))
        return self.schema(*values)

    @functools.lru_cache
    def ibis_types(self) -> tuple[dt.DataType, ...]:
        return tuple(self.ibis_schema().values())

    def pyarrow_to_ibis(self, table: ibis.Table) -> ibis.Table:
        schema = self.ibis_schema()
        upgrades = {col: pyarrow_to_ibis(table[col], t) for col, t in schema.items()}
        return table.mutate(**upgrades)

    def ibis_to_pyarrow(self, table: ibis.Table) -> ibis.Table:
        schema = self.ibis_schema()
        downgrades = {col: ibis_to_pyarrow(table[col], t) for col, t in schema.items()}
        return table.mutate(**downgrades)

    @functools.lru_cache
    def ibis_schema(self) -> ibis.Schema:
        return ibis.schema(self.schema.table_schema)


def py_to_pyarrow(value: Any, /, typ: dt.DataType) -> Any:
    """Convert Python types to PyArrow compatible types."""
    if value is None:
        return None

    match typ:
        case dt.UUID():
            return str(value)
        case dt.JSON():
            return json.dumps(value, indent=None, separators=(",", ":"))
        case dt.Array():
            return [
                py_to_pyarrow(v, typing_cast(dt.DataType, typ.value_type))
                for v in value
            ]
        case dt.Map():
            return {
                py_to_pyarrow(
                    key, typing_cast(dt.DataType, typ.key_type)
                ): py_to_pyarrow(val, typing_cast(dt.DataType, typ.value_type))
                for key, val in value.items()
            }
        case dt.Struct():
            raise TypeError(STRUCT_NOT_SUPPORTED)
        case _:
            return value


def pyarrow_to_py(value: Any, typ: dt.DataType) -> Any:
    """Restore Python types from PyArrow compatible types."""
    if value is None:
        return None

    match typ:
        case dt.UUID():
            return uuid.UUID(value)
        case dt.JSON():
            return json.loads(value)
        case dt.Array():
            return [
                pyarrow_to_py(val, typing_cast(dt.DataType, typ.value_type))
                for val in value
            ]
        case dt.Map():
            return {
                pyarrow_to_py(
                    key, typing_cast(dt.DataType, typ.key_type)
                ): pyarrow_to_py(val, typing_cast(dt.DataType, typ.value_type))
                for key, val in value
            }
        case dt.Struct():
            raise TypeError(STRUCT_NOT_SUPPORTED)
        case _:
            return value


def pyarrow_to_ibis(value: ir.Value, typ: dt.DataType) -> ir.Value:
    """Restore Ibis types from PyArrow compatible types."""
    match typ:
        case dt.UUID():
            assert isinstance(value, ir.StringValue)
            return value.cast(dt.UUID)
        case dt.JSON():
            assert isinstance(value, ir.StringValue)
            return value @ JsonParse()
        case dt.Array():
            assert isinstance(value, ir.ArrayValue)
            return value.map(
                lambda val: pyarrow_to_ibis(
                    val, typing_cast(dt.DataType, typ.value_type)
                )
            )
        case dt.Map():
            assert isinstance(value, ir.MapValue)
            return ibis.map(
                value.keys().map(
                    lambda val: pyarrow_to_ibis(
                        val, typing_cast(dt.DataType, typ.key_type)
                    )
                ),
                value.values().map(
                    lambda val: pyarrow_to_ibis(
                        val, typing_cast(dt.DataType, typ.value_type)
                    )
                ),
            )
        case dt.Struct():
            raise TypeError(STRUCT_NOT_SUPPORTED)
        case _:
            return operations.Cast(op_cast(value), to=typ).to_expr()


def ibis_to_pyarrow(value: ir.Value, typ: dt.DataType) -> ir.Value:
    """Downgrade Ibis types to PyArrow compatible types."""
    match typ:
        case dt.UUID():
            assert isinstance(value, ir.UUIDValue)
            return value.cast(str)
        case dt.JSON():
            assert isinstance(value, ir.JSONValue)
            return value @ JsonFormat()
        case dt.Array():
            assert isinstance(value, ir.ArrayValue)
            return value.map(
                lambda val: ibis_to_pyarrow(
                    val, typing_cast(dt.DataType, typ.value_type)
                )
            )
        case dt.Map():
            assert isinstance(value, ir.MapValue)
            return ibis.map(
                value.keys().map(
                    lambda val: ibis_to_pyarrow(
                        val, typing_cast(dt.DataType, typ.key_type)
                    )
                ),
                value.values().map(
                    lambda val: ibis_to_pyarrow(
                        val, typing_cast(dt.DataType, typ.value_type)
                    )
                ),
            )
        case dt.Struct():
            raise TypeError(STRUCT_NOT_SUPPORTED)
        case _:
            return operations.Cast(op_cast(value), to=typ).to_expr()
