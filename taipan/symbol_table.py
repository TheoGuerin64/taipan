from dataclasses import dataclass, field

from taipan.exceptions import TaipanSemanticError
from taipan.utils import Location


@dataclass
class SymbolTable:
    symbols: dict[str, Location] = field(default_factory=dict)

    def define(self, name: str, location: Location) -> None:
        if name in self.symbols:
            raise TaipanSemanticError(location, f"{name} already defined in this scope")

        self.symbols[name] = location

    def lookup(self, name: str) -> Location | None:
        return self.symbols.get(name)
