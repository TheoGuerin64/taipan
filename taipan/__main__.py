import os
import subprocess
import tempfile
from pathlib import Path

import click

from . import compile

INPUT_TYPE = click.Path(exists=True, dir_okay=False, readable=True, path_type=Path)
OUTPUT_TYPE = click.Path(exists=False, dir_okay=False, writable=True, path_type=Path)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("input", type=INPUT_TYPE)
@click.option("-o", "--output", type=OUTPUT_TYPE, default=Path.cwd().name, show_default=True)
@click.option("-c", type=click.BOOL, is_flag=True, default=False, help="Output C code")
def build(input: Path, output: Path, c: bool) -> None:
    compile(input, output, c)


@cli.command()
@click.argument("input", type=INPUT_TYPE)
@click.argument("args", nargs=-1, type=click.STRING)
def run(input: Path, output: Path, args: tuple[str]) -> None:
    path = tempfile.mkdtemp()
    try:
        compile(input, Path(path), False)
        subprocess.call([path, *args])
    finally:
        os.remove(path)


cli()
