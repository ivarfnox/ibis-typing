"""Provides ibis.Value -> ibis.Value functions for custom operations."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

import ibis
from ibis import Table, Value, ir

from .custom import custom_operations
from .custom.op_cast import op_cast
from .ibis_extension_method import (
    BooleanMethod,
    IntegerMethod,
    JSONMethod,
    StringMethod,
    UUIDMethod,
)


def column_checksum(value: Value) -> ir.IntegerValue:
    return value @ ColumnChecksum()


class ColumnChecksum(IntegerMethod):
    def apply(self, value: Value):
        return custom_operations.ColumnChecksum(arg=op_cast(value)).to_expr()


def literal_table(name: str, rows: Sequence, schema: ibis.Schema) -> Table:
    return custom_operations.LiteralTable.from_rows(
        rows,
        schema=schema,
        name=name,
    ).to_expr()


class JsonParse(JSONMethod):
    def apply(self, value: ir.StringValue):
        return custom_operations.JsonParse(arg=cast(Any, value)).to_expr()


def parse_json(value: ir.StringValue) -> ir.JSONValue:
    return value @ JsonParse()


class JsonFormat(StringMethod):
    """
    Format a JSON object as a string.

    Since .cast("string") is handled differently for JSON objects for different backends,
    this operation ensures that objects can be converted to strings for all backends.
    """

    def apply(self, value: ir.JSONValue):
        return custom_operations.JsonFormat(arg=op_cast(value)).to_expr()


def json_format(value: ir.JSONValue) -> ir.StringValue:
    return value @ JsonFormat()


class IntToUUID(UUIDMethod):
    def apply(self, value: ir.IntegerValue):
        return custom_operations.UUIDFromInt(arg=op_cast(value)).to_expr()


def uuid_from_int(value: ir.IntegerValue) -> ir.UUIDValue:
    return value @ IntToUUID()


class LuhnCheck(BooleanMethod):
    """
    Validate a string using the Luhn algorithm (e.g., credit card numbers).

    Trino has a built-in luhn_check() function. DuckDB uses a custom implementation
    that splits the string, reverses it, doubles every second digit, and checks
    if the sum modulo 10 equals 0.
    """

    def apply(self, value: ir.StringValue):
        return custom_operations.LuhnCheck(arg=op_cast(value)).to_expr()


def luhn_check(value: ir.StringValue) -> ir.BooleanValue:
    return value @ LuhnCheck()
