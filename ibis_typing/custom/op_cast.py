"""Work-around for `ibis.expr.operations` types."""

from typing import cast, overload

from ibis import ir
from ibis.expr import datatypes as dt
from ibis.expr.operations import Value


# Primitives
@overload
def op_cast(col: ir.BooleanValue) -> Value[dt.Boolean]: ...
@overload
def op_cast(col: ir.IntegerValue) -> Value[dt.Integer]: ...
@overload
def op_cast(col: ir.FloatingValue) -> Value[dt.Floating]: ...
@overload
def op_cast(col: ir.BinaryValue) -> Value[dt.Binary]: ...
@overload
def op_cast(col: ir.StringValue) -> Value[dt.String]: ...
# Complex types
@overload
def op_cast(col: ir.TimestampValue) -> Value[dt.Timestamp]: ...
@overload
def op_cast(col: ir.DateValue) -> Value[dt.Date]: ...
@overload
def op_cast(col: ir.TimeValue) -> Value[dt.Time]: ...
@overload
def op_cast(col: ir.DecimalValue) -> Value[dt.Decimal]: ...
# Collections
@overload
def op_cast(col: ir.ArrayValue) -> Value[dt.Array]: ...
@overload
def op_cast(col: ir.MapValue) -> Value[dt.Map]: ...
# Non-typed collections
@overload
def op_cast(col: ir.JSONValue) -> Value[dt.JSON]: ...
@overload
def op_cast(col: ir.StructValue) -> Value[dt.Struct]: ...
# Other
@overload
def op_cast(col: ir.Value) -> Value: ...


def op_cast(col: ir.Value) -> Value:
    """Work-around for `ibis.expr.operations` types."""
    return cast(Value, col)
