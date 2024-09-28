from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Position:
    line: int
    column: int


@dataclass(frozen=True)
class Location:
    file: Path
    start: Position
    end: Position
