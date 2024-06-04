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
@click.option("-c", type=click.BOOL, is_flag=True, default=False, help="Output C code")
def build(input: Path, output: Path | None, c: bool) -> None:
    if output is None:
        output = Path(input.name.removesuffix(".tp"))

    try:
        if c:
            compiler.compile_to_c(input, output)
        else:
            compiler.compile(input, output)
    except TaipanError as error:
        raise click.ClickException(str(error))


@cli.command()
@click.argument("input", type=click.Path(path_type=Path))
@click.argument("args", type=click.STRING, nargs=-1)
def run(input: Path, args: tuple[str]) -> None:
    try:
        compiler.run(input, args)
    except TaipanError as error:
        raise click.ClickException(str(error))


if __name__ == "__main__":
    cli()
