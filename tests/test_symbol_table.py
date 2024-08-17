from pathlib import Path

import pytest

from taipan.symbol_table import SymbolTable, TaipanSemanticError
from taipan.utils import Location

TP_FILE = Path("file.tp")
LOCATION = Location(TP_FILE, 1, 1)


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
