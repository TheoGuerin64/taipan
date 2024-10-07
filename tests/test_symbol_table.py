import pytest

from taipan.location import Location, Position
from taipan.symbol_table import SymbolTable, TaipanSemanticError

LOCATION = Location(
    None,
    start=Position(line=1, column=1),
    end=Position(line=1, column=2),
)


class TestSymbolTable:
    def test_declaration_lookup(self) -> None:
        table = SymbolTable()

        table.define("a", LOCATION)
        assert table.lookup("a") is LOCATION

    def test_redeclaration(self) -> None:
        table = SymbolTable()
        table.define("a", LOCATION)

        with pytest.raises(TaipanSemanticError):
            table.define("a", LOCATION)

    def test_undeclared(self) -> None:
        table = SymbolTable()
        assert table.lookup("a") is None
