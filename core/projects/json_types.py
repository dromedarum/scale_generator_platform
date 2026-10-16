from __future__ import annotations

from typing import TypeAlias

JsonScalar: TypeAlias = (
    str
    |int
    |float
    |bool
    |None
)

JsonValue: TypeAlias = (
    JsonScalar
    |list["JsonValue"]
    |dict[str, "JsonValue"]
)

def validate_json_value(
        value: object,
        *,
        path: str = "metadata",
) -> None:

    if value is None:
        return

    if isinstance(value,(str,int,float,bool)):
        return

    if isinstance(value,list):
        for index, item in enumerate(value):
            validate_json_value(item, path=f"{path}{index}")
            return

    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{path} contains a non-string key: {key!r}")

            validate_json_value(item, path=f"{path}.{key}")

        return

    raise TypeError(f"{path} containss a non-JSON-compatible value of type {type(value).__name__}.")