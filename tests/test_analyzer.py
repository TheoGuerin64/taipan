from pathlib import Path

import pytest

from taipan.analyzer import analyze
from taipan.exceptions import TaipanSemanticError
from taipan.parser import Parser


class TestAnalyzer:
    def compile_and_analyze(self, file: Path, code: str) -> None:
        ast = Parser.parse(file)
        analyze(ast.root)

    def test_redefine(self, tmp_path: Path) -> None:
        code = """\
        {
            let a = 1
            let a = 2
        }
        """

        file = tmp_path / "file.tp"
        file.write_text(code)

        with pytest.raises(TaipanSemanticError):
            self.compile_and_analyze(file, code)

    def test_undeclared(self, tmp_path: Path) -> None:
        code = """\
        {
            print a
        }
        """

        file = tmp_path / "file.tp"
        file.write_text(code)

        with pytest.raises(TaipanSemanticError):
            self.compile_and_analyze(file, code)

    def test_defined_after(self, tmp_path: Path) -> None:
        code = """\
        {
            print a
            let a = 1
        }
        """

        file = tmp_path / "file.tp"
        file.write_text(code)

        with pytest.raises(TaipanSemanticError):
            self.compile_and_analyze(file, code)

    def test_higher_scope_declaration(self, tmp_path: Path) -> None:
        code = """\
        {
            {
                let a = 1
            }
            print a
        }
        """

        file = tmp_path / "file.tp"
        file.write_text(code)

        with pytest.raises(TaipanSemanticError):
            self.compile_and_analyze(file, code)

    def test_higher_scope_usage(self, tmp_path: Path) -> None:
        code = """\
        {
            let a = 1
            {
                print a
            }
        }
        """

        file = tmp_path / "file.tp"
        file.write_text(code)

        self.compile_and_analyze(file, code)

    def test_in_between_scope(self, tmp_path: Path) -> None:
        code = """\
        {
            let a = 1
            {}
            print a
        }
        """

        file = tmp_path / "file.tp"
        file.write_text(code)

        self.compile_and_analyze(file, code)

    def test_redefinition_inner_scope(self, tmp_path: Path) -> None:
        code = """\
        {
            let a = 1
            {
                let a = 2
            }
            print a
        }
        """

        file = tmp_path / "file.tp"
        file.write_text(code)

        self.compile_and_analyze(file, code)
