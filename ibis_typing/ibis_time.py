"""Time operations for `ibis.Table` expressions."""

from __future__ import annotations

import datetime
from typing import Self, cast

import ibis
from attrs import frozen
from ibis import ir, literal
from ibis.common.temporal import DateUnit
from ibis.expr import datatypes as dt

from ibis_typing.ibis_extension_method import DateMethod, IntegerMethod

from . import ibis_types as it
from .custom.custom_operations import DateAddDay, DateAddMonth
from .custom.op_cast import op_cast
from .expression import Expression
from .ibis_adapter import IbisTable


@frozen
class TimestampNow(Expression):
    """Table with current timestamp used for functional programming."""

    timestamp: it.Timestamp = None

    table_schema = {  # noqa: RUF012
        "timestamp": "timestamp(6)",
    }

    @classmethod
    def from_expression(cls):
        return cls.as_of()

    @classmethod
    def as_of(cls, timestamp: datetime.datetime | None = None) -> IbisTable[Self]:
        if timestamp:
            return cls.of_rows([cls(timestamp)])
        table = cls.of_rows([cls()]).table
        table = table.mutate(**{str(cls.cols.timestamp): now()})
        return cls.of(table)

    @classmethod
    def as_scalar(cls, table: IbisTable[Self]) -> ibis.ir.TimestampScalar:
        scalar = table.table[cls.cols.timestamp].as_scalar()
        return cast(ibis.ir.TimestampScalar, scalar)


@frozen
class StartOfMonth(DateMethod):
    def apply(self, value: ir.DateValue):
        return truncate_month(value)


@frozen
class MonthsSince(IntegerMethod):
    start: ir.DateValue | datetime.date

    def apply(self, value: ir.DateValue):
        return diff_months(value, self.start)


@frozen
class DaysSince(IntegerMethod):
    start: ir.DateValue | datetime.date

    def apply(self, value: ir.DateValue):
        return diff_days(value, self.start)


@frozen
class AddMonths(DateMethod):
    months: ir.IntegerValue | int

    def apply(self, value: ir.DateValue):
        return add_months(value, self.months)


@frozen
class AddDays(DateMethod):
    days: ir.IntegerValue | int

    def apply(self, value: ir.DateValue):
        return add_days(value, self.days)


def now() -> ir.TimestampValue:
    """Get current timestamp.

    Can be mocked by test fixture.
    For functional programming, use NowTimestamp as a table input.
    """
    timestamp = ibis.now().cast("timestamp(6)")
    return cast(ir.TimestampValue, timestamp)


def truncate_month(date: ir.DateValue) -> ir.DateValue:
    return date.truncate(DateUnit.MONTH)  # type: ignore


def _coerce_date(d: ir.DateValue | datetime.date) -> ir.DateValue:
    if isinstance(d, datetime.date):
        return literal(d)
    return d


def _coerce_int(n: ir.IntegerValue | int) -> ir.IntegerValue:
    if isinstance(n, int):
        return literal(n)
    return n


def diff_months(
    end: ir.DateValue, start: ir.DateValue | datetime.date
) -> ir.IntegerValue:
    return end.delta(_coerce_date(start), unit="month")


def diff_days(
    end: ir.DateValue, start: ir.DateValue | datetime.date
) -> ir.IntegerValue:
    return end.delta(_coerce_date(start), unit="day")


def add_months(date: ir.DateValue, months: ir.IntegerValue | int) -> ir.DateValue:
    """Add months to a date, returning a new date at start of month.

    Note: Work-around for Ibis using `datetime.date`
    which only supports fixed-length intervals, that is, not months.
    """
    return DateAddMonth(
        op_cast(truncate_month(date)), op_cast(_coerce_int(months))
    ).to_expr()


def add_days(date: ir.DateValue, days: ir.IntegerValue | int) -> ir.DateValue:
    """Add days to a date, returning a new date.

    Note: Work-around for Ibis using `datetime.date`
    """
    return DateAddDay(
        op_cast(date), op_cast(_coerce_int(days).cast(dt.int32))
    ).to_expr()
