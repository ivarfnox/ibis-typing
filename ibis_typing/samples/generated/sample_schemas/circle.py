from attrs import frozen
from ibis_typing import IbisSchema
from ibis_typing.ibis_types import *

__all__ = [
    "Circle",
]


@frozen
class Circle(IbisSchema):
    diameter: Float32 = None
    area: Float64 = None
    circumference: Float64 = None

    table_schema = {
        "diameter": "float32",
        "area": "float64",
        "circumference": "float64",
    }
