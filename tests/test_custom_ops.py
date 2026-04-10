from __future__ import annotations

import json
import uuid

import ibis
from attrs import frozen

from ibis_typing import (
    Expression,
    IbisSchema,
    IbisTable,
    it,
    this,
)
from ibis_typing.fixtures.expressions import EvaluateTable
from ibis_typing.ibis_ops import IntToUUID, JsonFormat, LuhnCheck
from ibis_typing.ibis_utils import Select


@frozen
class InputJson(IbisSchema):
    json: it.JSON = None


@frozen
class JsonKey(Expression):
    key: it.Int64 = None

    @classmethod
    def from_expression(cls, inputs: IbisTable[InputJson]):
        col = inputs.cols
        table = inputs.table @ Select({"key": this[col.json]["key"].int})
        return cls.of(table)


@frozen
class JsonFormatExpr(Expression):
    json_format: it.String = None

    @classmethod
    def from_expression(cls, inputs: IbisTable[InputJson]):
        table = inputs.table @ Select(
            {"json_format": this[inputs.cols.json]["PropertyNested"] @ JsonFormat()},
        )
        return cls.of(table)


def test_parse_json(evaluate_table):
    actual, expected = evaluate_table(
        JsonKey,
        [
            InputJson(json={"key": 1}),
            JsonKey(key=1),
        ],
    )
    assert actual == expected


def test_json_format(evaluate_table):
    expected_nested_inside = {"Nested": "Inside"}

    input_json_obj = {"PropertyNested": expected_nested_inside}

    actual, _ = evaluate_table(
        JsonFormatExpr,
        [InputJson(json=input_json_obj)],
    )

    assert json.loads(actual[0].json_format) == expected_nested_inside


@frozen
class UUIDHashInput(IbisSchema):
    id_hash: it.Int64 = None


@frozen
class UUIDFromInt(Expression):
    id: it.UUID = None

    @classmethod
    def from_expression(cls, inputs: IbisTable[UUIDHashInput]):
        table = inputs.table @ Select(
            {"id": this[inputs.cols.id_hash] @ IntToUUID()},
        )
        return cls.of(table)


def test_uuid_from_int(evaluate_table):
    actual, expected = evaluate_table(
        UUIDFromInt,
        [
            UUIDHashInput(id_hash=1),
            UUIDHashInput(id_hash=-1),
            UUIDFromInt(id=uuid.UUID(hex="00000000-0000-0000-0000-000000000001")),
            UUIDFromInt(id=uuid.UUID(hex="00000000-0000-0000-ffff-ffffffffffff")),
        ],
    )

    assert actual == expected


@frozen
class InputUUID(IbisSchema):
    uuid: it.UUID = None


@frozen
class OutputUUID(Expression):
    uuid: it.Array[it.UUID] = None

    @classmethod
    def from_expression(cls, inputs: IbisTable[InputUUID]):
        table = inputs.table @ Select(
            expr={
                inputs.cols.uuid: ibis.array([this[inputs.cols.uuid]]),
            },
        )
        return cls.of(table)


def test_uuid_compatibility(evaluate_table):
    rows = [
        InputUUID(),
        InputUUID(uuid.UUID(int=1)),
        OutputUUID([None]),
        OutputUUID([uuid.UUID(int=1)]),
    ]
    actual, expected = evaluate_table(OutputUUID, rows)
    assert actual == expected


@frozen
class LuhnInput(IbisSchema):
    input_number: it.String = None


@frozen
class LuhnResult(Expression):
    is_valid: it.Boolean = None

    @classmethod
    def from_expression(
        cls: type[LuhnResult], inputs: IbisTable[LuhnInput]
    ) -> IbisTable[LuhnResult]:
        table = inputs.table @ Select(
            {"is_valid": this[inputs.cols.input_number] @ LuhnCheck()},
        )
        return cls.of(table)


def test_luhn_check(evaluate_table: EvaluateTable):
    actual, expected = evaluate_table(
        LuhnResult,
        [
            LuhnInput(input_number="8112189876"),
            LuhnInput(input_number="9503271414"),
            LuhnInput(input_number="9503271415"),
            LuhnResult(is_valid=True),
            LuhnResult(is_valid=True),
            LuhnResult(is_valid=False),
        ],
    )

    def luhn_key(luhn_result: LuhnResult) -> bool:
        return bool(luhn_result.is_valid)

    assert actual.sort(key=luhn_key) == expected.sort(
        key=luhn_key
    )  # Sort since ordering is not guaranteed for trino
