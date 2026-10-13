from dataclasses import dataclass
from typing import Any


@dataclass
class HyperuniformNetwork:

    seed_points: Any | None = None

    relaxed_points: Any | None = None

    vertices: Any | None = None

    edges: Any | None = None

    cells: Any | None = None
