from pathlib import Path

import click

from .compiler import compile


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
)
def taipan(input: Path, output: Path) -> None:
    compile(input, output)


taipan()
