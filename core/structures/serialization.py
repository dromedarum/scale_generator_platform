from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .parameters import StructureParameters
from .enums import StructureType, RidgeMode, RidgeRootMode

def save_structure_parameters(
        params: StructureParameters,
        filepath: str | Path,
) -> None:
    """
    Save StructureParameters to JSON.
    """
    data = asdict(params)
    #Convert enums to JSON-friendly strings
    data["structure_type"] = params.structure_type.value
    data["ridge_mode"] = params.ridge_mode.value
    data["ridge_root_mode"] =params.ridge_root_mode.value

    filepath = Path(filepath)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"Saved structure parameters to {filepath}")

def load_structure_parameters(
        filepath: str | Path,
) -> StructureParameters:
    """
    Load StructureParameters from JSON
    """
    filepathm = Path(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    #Convert string back into enums
    data["structure_type"] = StructureType(
        data["structure_type"]
    )

    data["ridge_mode"] = RidgeMode(
        data["ridge_mode"]
    )

    data["ridge_root_mode"] = RidgeRootMode(data["ridge_root_mode"])
    
    return StructureParameters(**data)

