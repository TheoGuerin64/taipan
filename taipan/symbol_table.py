from dataclasses import dataclass, field
from pathlib import Path

from .exceptions import TaipanSemanticError


@dataclass(frozen=True)
class Symbol:
    name: str
    line: int
    column: int


@dataclass
class SymbolTable:
    file: Path
    symbols: dict[str, Symbol] = field(default_factory=dict)

    def define(self, symbol: Symbol) -> None:
        if symbol.name in self.symbols.keys():
            raise TaipanSemanticError(
                self.file,
                symbol.line,
                symbol.column,
                f"{symbol.name} already defined in this scope",
            )

        self.symbols[symbol.name] = symbol

    def lookup(self, name: str) -> Symbol | None:
        return self.symbols.get(name)
