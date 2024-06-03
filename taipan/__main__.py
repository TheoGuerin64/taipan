import shutil
from pathlib import Path

import click

from . import compile


@click.command()
@click.argument(
    "input",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=False, dir_okay=False, writable=True, path_type=Path),
    default="a.out",
    show_default=True,
    help="Output file",
)
@click.option(
    "--gcc",
    type=click.Path(exists=True, dir_okay=False, executable=True, path_type=Path),
    default=shutil.which("gcc"),
    show_default=True,
    help="C compiler",
)
def taipan(input: Path, output: Path, gcc: Path | None) -> None:
    if gcc is None:
        raise click.ClickException("GCC not found")
    compile(input, output, gcc)


taipan()
