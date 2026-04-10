import math

from ibis_typing.samples.sample_transforms import Circle, CircleParameters
from ibis_typing.utils import ApproxFloat


def test_circle_calculations(evaluate_table):
    inputs = [
        CircleParameters(diameter=10.0),
    ]
    outputs = [
        Circle(
            diameter=p.diameter,
            area=p.diameter and p.diameter**2 * math.pi,
            circumference=p.diameter and p.diameter * 2 * math.pi,
        )
        for p in inputs
    ]
    rows = inputs + outputs
    actual, expected = evaluate_table(Circle, rows)

    expected_approx = [
        Circle(
            diameter=c.diameter,
            area=ApproxFloat(c.area),
            circumference=ApproxFloat(c.circumference),
        )
        for c in expected
    ]

    assert actual == expected_approx
