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
    symbols: set[Symbol] = field(default_factory=set)

    def define(self, symbol: Symbol) -> None:
        if symbol in self.symbols:
            raise TaipanSemanticError(
                self.file,
                symbol.line,
                symbol.column,
                f"{symbol.name} already defined in this scope",
            )

        self.symbols.add(symbol)

    def lookup(self, symbol: Symbol) -> bool:
        return symbol in self.symbols
