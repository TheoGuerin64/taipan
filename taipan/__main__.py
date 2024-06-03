import subprocess
import tempfile
from pathlib import Path

import click

from .compiler import compile
from .exceptions import TaipanException


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
        compile(input, output, compile_to_c=c)
    except TaipanException as error:
        raise click.ClickException(str(error))


@cli.command()
@click.argument("input", type=click.Path(path_type=Path))
@click.argument("args", type=click.STRING, nargs=-1)
def run(input: Path, args: tuple[str]) -> None:
    temp = Path(tempfile.mktemp())
    try:
        compile(input, temp)
    except TaipanException as error:
        temp.unlink(True)
        raise click.ClickException(str(error))

    subprocess.call([temp, *args])
    temp.unlink()


if __name__ == "__main__":
    cli()
