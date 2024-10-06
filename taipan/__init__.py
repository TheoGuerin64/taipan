from taipan._compiler import compile, compile_to_c, run
from taipan._parser import Parser

parse = Parser.parse


__all__ = ["compile", "compile_to_c", "run", "parse"]
