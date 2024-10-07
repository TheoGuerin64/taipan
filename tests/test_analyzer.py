from pathlib import Path

import pytest

from taipan import parse
from taipan._analyzer import Analyzer
from taipan.exceptions import TaipanSemanticError


class TestAnalyzer:
    def compile_and_analyze(self, code: str) -> None:
        ast = parse(code)
        Analyzer.analyze(ast)

    def test_redefine(self, tmp_path: Path) -> None:
        code = """\
        {
            let a = 1
            let a = 2
        }
        """

        with pytest.raises(TaipanSemanticError):
            self.compile_and_analyze(code)

    def test_undeclared(self, tmp_path: Path) -> None:
        code = """\
        {
            print a
        }
        """

        with pytest.raises(TaipanSemanticError):
            self.compile_and_analyze(code)

    def test_defined_after(self, tmp_path: Path) -> None:
        code = """\
        {
            print a
            let a = 1
        }
        """

        with pytest.raises(TaipanSemanticError):
            self.compile_and_analyze(code)

    def test_higher_scope_declaration(self, tmp_path: Path) -> None:
        code = """\
        {
            {
                let a = 1
            }
            print a
        }
        """

        with pytest.raises(TaipanSemanticError):
            self.compile_and_analyze(code)

    def test_higher_scope_usage(self, tmp_path: Path) -> None:
        code = """\
        {
            let a = 1
            {
                print a
            }
        }
        """

        self.compile_and_analyze(code)

    def test_in_between_scope(self, tmp_path: Path) -> None:
        code = """\
        {
            let a = 1
            {}
            print a
        }
        """

        self.compile_and_analyze(code)

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

        self.compile_and_analyze(code)
