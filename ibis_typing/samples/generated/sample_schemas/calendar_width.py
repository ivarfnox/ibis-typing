from attrs import frozen
from ibis_typing import IbisSchema
from ibis_typing.ibis_types import *

__all__ = [
    "CalendarWidth",
]


@frozen
class CalendarWidth(IbisSchema):
    checksum_updated_at: Timestamp = None
    day_span: Int64 = None

    table_schema = {
        "checksum_updated_at": "timestamp(6)",
        "day_span": "int64",
    }
