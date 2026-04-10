from attrs import frozen
from ibis_typing import IbisSchema
from ibis_typing.ibis_types import *

__all__ = [
    "CalendarChecksumBucket",
]


@frozen
class CalendarChecksumBucket(IbisSchema):
    checksum_updated_at: Timestamp = None
    checksum: Int64 = None

    table_schema = {
        "checksum_updated_at": "timestamp(6)",
        "checksum": "int64",
    }
