import sys
from pathlib import Path

import click

from taipan import _compiler


@click.group()
@click.version_option(None, "-v", "--version")
def cli() -> None:
    """Taipan programming language CLI"""


@cli.command()
@click.argument("input_", metavar="input", type=click.Path(path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path))
@click.option("-c", "compile_c", type=click.BOOL, is_flag=True, default=False, help="Output C code")
@click.option("-O", "optimize", type=click.BOOL, is_flag=True, default=False, help="Optimize")
def build(input_: Path, output: Path | None, compile_c: bool, optimize: bool) -> None:
    """Compile Taipan code to C or binary"""
    if output is None:
        output = Path(input_.name).with_suffix("")

    if compile_c:
        _compiler.compile_to_c(input_, output)
    else:
        _compiler.compile(input_, output, optimize)


@cli.command()
@click.argument("input_", metavar="input", type=click.Path(path_type=Path))
@click.argument("args", type=click.STRING, nargs=-1)
@click.option("-O", "optimize", type=click.BOOL, is_flag=True, default=False, help="Optimize")
def run(input_: Path, args: tuple[str, ...], optimize: bool) -> None:
    """Run Taipan code with arguments"""
    exit_code = _compiler.run(input_, args, optimize)
    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
