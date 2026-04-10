from __future__ import annotations

import inspect
from types import FunctionType, MethodType
from typing import cast


def get_self_methods(cls: type) -> list[MethodType]:
    from typing import Self

    return_types = cls, cast(type, Self)

    return get_methods(cls, *return_types)


def get_methods(cls: type, *return_types: type) -> list[MethodType]:
    methods = [
        method for name, method in vars(cls).items() if inspect.isfunction(method)
    ]
    return_names = {type_.__name__ for type_ in return_types}
    return [
        cast(MethodType, method)
        for method in methods
        if not return_names or return_type_name(method) in return_names
    ]


def return_type_name(method: MethodType | FunctionType) -> str | None:
    qualified_type_name = inspect.get_annotations(method).get("return")
    if not qualified_type_name:
        return None

    return qualified_type_name.split(".")[-1]
