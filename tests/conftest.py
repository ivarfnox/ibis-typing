from __future__ import annotations

import datetime

import hypothesis
from attrs import frozen

from ibis_typing import IbisSchema, it
from ibis_typing.fixtures import marks, plugin

local_plugins = plugin.pytest_plugins

pytest_plugins = local_plugins


hypothesis.settings.register_profile(
    marks.IbisBackends.duck,
    suppress_health_check=[hypothesis.HealthCheck.function_scoped_fixture],
    max_examples=8,
    deadline=datetime.timedelta(milliseconds=1_000),
)
hypothesis.settings.register_profile(
    marks.IbisBackends.trino,
    suppress_health_check=[hypothesis.HealthCheck.function_scoped_fixture],
    max_examples=4,
    deadline=datetime.timedelta(milliseconds=4_000),
)
hypothesis.settings.load_profile(
    str(marks.TEST_IBIS_BACKEND or marks.IbisBackends.trino)
)


@frozen
class SimpleSchema(IbisSchema):
    id: it.Int64
    value: it.Int64
