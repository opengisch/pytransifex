from typing import Any

import click

from pytransifex.api_new import Transifex

client = Transifex(defer_login=True)


def format_args(args: dict[str, Any]) -> dict[str, Any]:
    return {k.replace("-", "_"): v for k, v in args.items()}


@click.group()
def cli():
    pass


@click.option("--verbose", is_flag=True, default=False)
@click.argument("file_name", required=True)
@cli.command("push", help="Push translation strings")
def push(file_name: str, verbose: bool):
    click.echo(f"Pushing: {file_name}")
    client.push()
    if verbose:
        click.echo("Was it verbose enough?")


@click.option("--only-lang", "-l", default="all")
@click.argument("dir_name", required=True)
@cli.command("pull", help="Pull translation strings")
def pull(dir_name: str, only_lang: str):
    client.pull()
    click.echo(f"Pulling: {dir_name}, {only_lang}")


if __name__ == "__main__":
    cli()
