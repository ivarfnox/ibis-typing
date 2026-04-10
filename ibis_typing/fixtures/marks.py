"""Marks for partitioning pytest runs."""

from __future__ import annotations

import os
from enum import StrEnum
from typing import cast

import pytest

_TEST_IBIS_BACKEND = os.environ.get("TEST_IBIS_BACKEND")

# Markers for tests depending on specific Ibis backend connections.
ibis = pytest.mark.ibis
trino = pytest.mark.trino
duck = pytest.mark.duck


class IbisBackends(StrEnum):
    duck = "duck"
    trino = "trino"


TEST_IBIS_BACKEND = cast(
    IbisBackends | None,
    _TEST_IBIS_BACKEND and IbisBackends(_TEST_IBIS_BACKEND),
)


select_backend_for_test: pytest.MarkDecorator = pytest.mark.use_backend
deselect_backend_for_test: pytest.MarkDecorator = pytest.mark.skip_backend

use_backend_duckdb = select_backend_for_test(IbisBackends.duck)
use_backend_trino = select_backend_for_test(IbisBackends.trino)

skip_duckdb = deselect_backend_for_test(IbisBackends.duck)
