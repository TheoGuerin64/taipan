from pathlib import Path

import click

from . import compiler
from .exceptions import TaipanError


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("input", type=click.Path(path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path))
@click.option("-c", "compile_c", type=click.BOOL, is_flag=True, default=False, help="Output C code")
@click.option("-O", "optimize", type=click.BOOL, is_flag=True, default=False, help="Optimize")
def build(input: Path, output: Path | None, compile_c: bool, optimize: bool) -> None:
    if output is None:
        output = Path(input.name.removesuffix(".tp"))

    try:
        if compile_c:
            compiler.compile_to_c(input, output)
        else:
            compiler.compile(input, output, optimize)
    except TaipanError as error:
        raise click.ClickException(str(error))


@cli.command()
@click.argument("input", type=click.Path(path_type=Path))
@click.argument("args", type=click.STRING, nargs=-1)
@click.option("-O", "optimize", type=click.BOOL, is_flag=True, default=False, help="Optimize")
def run(input: Path, args: tuple[str], optimize: bool) -> None:
    output_name = input.with_suffix("").name

    try:
        compiler.run(input, output_name, args, optimize)
    except TaipanError as error:
        raise click.ClickException(str(error))


if __name__ == "__main__":
    cli()
