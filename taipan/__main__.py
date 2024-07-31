from pathlib import Path

import click

from taipan import compiler


@click.group()
def cli() -> None:
    """Taipan programming language CLI"""


@cli.command()
@click.argument("input", type=click.Path(path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path))
@click.option("-c", "compile_c", type=click.BOOL, is_flag=True, default=False, help="Output C code")
@click.option("-O", "optimize", type=click.BOOL, is_flag=True, default=False, help="Optimize")
def build(input: Path, output: Path | None, compile_c: bool, optimize: bool) -> None:
    """Compile Taipan code to C or binary"""
    if output is None:
        output = Path(input.name.removesuffix(".tp"))

    if compile_c:
        compiler.compile_to_c(input, output)
    else:
        compiler.compile(input, output, optimize)


@cli.command()
@click.argument("input", type=click.Path(path_type=Path))
@click.argument("args", type=click.STRING, nargs=-1)
@click.option("-O", "optimize", type=click.BOOL, is_flag=True, default=False, help="Optimize")
def run(input: Path, args: tuple[str, ...], optimize: bool) -> None:
    """Run Taipan code with arguments"""
    output_name = input.with_suffix("").name
    compiler.run(input, output_name, args, optimize)


if __name__ == "__main__":
    cli()
