from dataclasses import asdict
from os import mkdir, rmdir
from pathlib import Path

import click

from pytransifex.api_new import Transifex
from pytransifex.config import CliSettings

client = Transifex(defer_login=True)
cli_settings: CliSettings | None = None


@click.group(chain=True)
@click.pass_context
def cli(ctx):
    ctx.obj = {}


@click.option("-v", "--verbose", is_flag=True, default=False)
@click.option("-out", "--output-dir", is_flag=False)
@click.option("-in", "--input-dir", is_flag=False)
@click.option("-org", "--organization-slug", is_flag=False)
@click.option("-p", "--project-slug", is_flag=False)
@cli.command(
    "init", help="Initialize the CLI with the appropriate configuration values."
)
@click.pass_context
def init(ctx, **opts):
    mandatory = ["organization_slug", "project_slug"]
    if missing := [k for k in mandatory if not k in opts]:
        raise Exception(
            f"These keys are not set or do not have a well-defined value: {', '.join(missing)}"
        )
    if empty := [k for k, v in opts.items() if k in mandatory and not v]:
        raise Exception(f"These keys have an empty value: {', '.join(empty)}")

    organization_slug = opts["organization_slug"]
    project_slug = opts["project_slug"]

    input_directory = opts.get("input_dir")
    output_directory = opts.get("input_dir")
    input_directory = Path(input_directory) if input_directory else Path.cwd()
    output_directory = (
        Path(output_directory)
        if output_directory
        else Path.cwd().joinpath("downloaded_files")
    )

    has_to_create_dir = not Path.exists(output_directory)
    reply = ""

    try:
        click.echo(f"Initializing...")

        if has_to_create_dir:   
            mkdir(output_directory)

        settings = asdict(CliSettings(
            organization_slug, project_slug, input_directory, output_directory
        ))
        
        for k, v in settings.items():
            ctx.obj[k] = v
        
        reply += f"Initialized project with the following settings: {project_slug}. "

    except Exception as error:
        reply += f"Failed to initialize the CLI, this error occurred: {error} "

        if has_to_create_dir:
            rmdir(output_directory)

        reply += f"Removed {output_directory}. "

    finally:
        click.echo(reply)


@click.argument("input-directory", required=False)
@cli.command("push", help="Push translation strings")
@click.pass_context
def push(ctx, input_directory: str | None):
    print(f"CONTEXT from PUSH: {ctx.obj}")
    if input_directory:
        ctx.obj["input_directory"] = Path(input_directory)

    resource_slugs = [""]
    path_to_files = list(
        Path.iterdir(
            ctx.obj["input_directory"]
            if "input_directory" in ctx.obj
            else Path.cwd()
        )
    )
    reply = ""

    try:
        click.echo(
            f"Pushing {resource_slugs} from {path_to_files} to Transifex under project {ctx.obj['project_slug']}..."
        )
        # client.push(project_slug=ctx.project_slug, resource_slugs=resource_slugs, path_to_files=path_to_files)
    except Exception as error:
        reply += f"Failed because of this error: {error}"
    finally:
        click.echo(reply)


@click.option("-l", "--only-lang", default="all")
@click.argument("output-directory", required=False)
@cli.command("pull", help="Pull translation strings")
@click.pass_context
def pull(ctx, output_directory: str | None, only_lang: str | None):
    print(f"CONTEXT from PULL: {ctx.obj}")
    if output_directory:
        ctx.obj["output_dir"] = output_directory

    resource_slugs = []
    reply = ""
    language_codes = only_lang.split(",") if only_lang else []

    try:
        click.echo(
            f"Pulling translation strings from project {ctx.obj['project_slug']} to {output_directory}..."
        )
        # client.pull(project_slug=ctx.project_slug, resource_slugs=resource_slugs, language_codes=language_codes, output_dir=ctx.output_dir)
    except Exception as error:
        reply += f"Failed because of this error: {error}"
    finally:
        click.echo(reply)


if __name__ == "__main__":
    cli()
