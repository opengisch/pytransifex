from typing import Any
import click

from pytransifex.api import Transifex


def format_args(args: dict[str, Any]) -> dict[str, Any]:
    return {k.replace("-", "_"): v for k, v in args.items()}


@click.command()
@click.argument("f_name")
@click.option("--dry-run", type=bool)
@click.option("--outsource-project-name", type=str)
@click.option("--private", type=bool)
@click.option("--path-to-file", type=str)
@click.option("--project-name", type=str)
@click.option("--project-slug", type=str)
@click.option("--repository-url", type=str)
@click.option("--resource-name", type=str)
@click.option("--resource-slug", type=str)
@click.option("--source-lang-code", type=str)
def run_cli(f_name: str, **options):
    translator = Transifex.get()
    result = translator.exec(f_name, format_args(options))
    click.echo(result)
