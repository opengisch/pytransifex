from typing import Any
import click

from pytransifex.api import Transifex
from pytransifex.config import Config


def format_args(args: dict[str, Any]) -> dict[str, Any]:
    return {k.replace("-", "_"): v for k, v in args.items()}


import click


@click.group()
def cli():
    pass


@click.option("--verbose", is_flag=True, default=False)
@click.argument("file_name", required=True)
@cli.command("push", help="Push documentation")
def push(file_name: str, verbose: bool):
    click.echo(f"push: {file_name}")
    if verbose:
        click.echo("Was it verbose enough?")


@click.option("--only-lang", "-l", default="all")
@click.argument("dir_name", required=True)
@cli.command("pull", help="Pull documentation")
def pull(dir_name: str, only_lang: str):
    click.echo(f"pull: {dir_name}, {only_lang}")


if __name__ == "__main__":
    cli()
