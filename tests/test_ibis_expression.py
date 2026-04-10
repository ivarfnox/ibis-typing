from attrs import frozen

from ibis_typing import IbisSchema, it, this
from ibis_typing.expression import TableExpression
from ibis_typing.ibis_adapter import IbisTable
from ibis_typing.ibis_utils import Select


@frozen
class SimpleSchema(IbisSchema):
    value: it.Int64 = None


class SimpleTableExpression(TableExpression):
    def __call__(self, inputs: IbisTable[SimpleSchema]):
        return inputs.table @ Select(
            {inputs.cols.value: this[inputs.cols.value].cast(float) / 2}
        )


def test_simple_transform(evaluate_table):
    inputs = [SimpleSchema(1)]
    SimpleTransform = SimpleTableExpression().as_expression_schema()
    outputs = [SimpleTransform(0.5)]
    actual, expected = evaluate_table(SimpleTransform, [*inputs, *outputs])
    assert actual == expected
