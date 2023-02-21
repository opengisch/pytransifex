import logging
import traceback
from os import mkdir, rmdir
from pathlib import Path

import click

from pytransifex.api import Transifex
from pytransifex.config import CliSettings

logger = logging.getLogger(__name__)
client = Transifex(defer_login=True)
assert client


def path_to_slug(file_paths: list[Path]) -> list[str]:
    keep_last = (str(f).split("/")[-1] for f in file_paths)
    remove_dot = (s.split(".")[0] for s in keep_last)
    return list(remove_dot)


def extract_files(input_dir: Path) -> tuple[list[Path], list[str], str]:
    files = list(Path.iterdir(input_dir))
    slugs = path_to_slug(files)
    files_status_report = "\n".join(
        (f"file: {file} => slug: {slug}" for slug, file in zip(slugs, files))
    )
    return (files, slugs, files_status_report)


@click.group
def cli():
    pass


@click.option("-v", "--verbose", is_flag=True, default=False)
@click.option("-out", "--output-directory", is_flag=False)
@click.option("-in", "--input-directory", is_flag=False)
@click.option("-org", "--organization-slug", is_flag=False)
@click.option("-p", "--project-slug", is_flag=False)
@cli.command(
    "init", help="Initialize the CLI with the appropriate configuration values."
)
def init(**opts):
    reply = ""
    settings = CliSettings.extract_settings(**opts)
    has_to_create_dir = not Path.exists(settings.output_directory)

    try:
        click.echo(f"Initializing...")

        if has_to_create_dir:
            mkdir(settings.output_directory)

        reply += f"Initialized project with the following settings: {settings.project_slug} and saved file to {settings.config_file} "

        if not settings.input_directory:
            reply += f"WARNING: You will need to declare an input directory if you plan on using 'pytx push', as in 'pytx push --input-directory <PATH/TO/DIRECTORY>'."

    except Exception as error:
        reply += (
            f"cli:init > Failed to initialize the CLI, this error occurred: {error}."
        )

        if has_to_create_dir:
            rmdir(settings.output_directory)

        reply += f"Removed {settings.output_directory}. "

    finally:
        click.echo(reply)
        settings.to_disk()


@click.option("-in", "--input-directory", is_flag=False)
@cli.command("push", help="Push translation strings")
def push(input_directory: str | None):
    reply = ""
    settings = CliSettings.from_disk()
    input_dir = (
        Path.cwd().joinpath(input_directory)
        if input_directory
        else getattr(settings, "input_directory", None)
    )

    if not input_dir:
        raise FileExistsError(
            "cli:push > To use this 'push', you need to initialize the project with a valid path to the directory containing the files to push; alternatively, you can call this commend with 'pytx push --input-directory <PATH/TO/DIRECTORY>'."
        )

    try:
        files, slugs, files_status_report = extract_files(input_dir)
        click.echo(
            f"cli:push > Pushing {files_status_report} to Transifex under project {settings.project_slug}."
        )
        client.push(
            project_slug=settings.project_slug,
            resource_slugs=slugs,
            path_to_files=[str(f) for f in files],
        )
    except Exception as error:
        reply += f"cli:push > Failed because of this error: {error}"
        logging.error(f"traceback: {traceback.print_exc()}")
    finally:
        click.echo(reply)
        settings.to_disk()


@click.option("-l", "--only-lang", default="all")
@click.option("-out", "--output-directory", is_flag=False)
@cli.command("pull", help="Pull translation strings")
def pull(output_directory: str | None, only_lang: str | None):
    reply = ""
    settings = CliSettings.from_disk()
    language_codes = only_lang.split(",") if only_lang else []

    if output_directory:
        settings.output_directory = Path(output_directory)
    else:
        output_directory = str(settings.output_directory)

    resource_slugs = []
    try:
        click.echo(
            f"Pulling translation strings ({language_codes}) from project {settings.project_slug} to {str(output_directory)}..."
        )
        client.pull(
            project_slug=settings.project_slug,
            resource_slugs=resource_slugs,
            language_codes=language_codes,
            path_to_output_dir=output_directory,
        )
    except Exception as error:
        reply += f"cli:pull > failed because of this error: {error}"
        logging.error(f"traceback: {traceback.print_exc()}")
    finally:
        click.echo(reply)
        settings.to_disk()
