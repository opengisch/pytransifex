import glob
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from pytransifex.api import Transifex

logger = logging.getLogger(__name__)


@dataclass
class Parameters:
    changelog_include: Optional[bool] = False
    changelog_path: Optional[str] = None
    changelog_number_of_entries: Optional[int] = None
    create_date: Optional[date] = datetime.now()
    github_organization_slug: Optional[str] = None
    lrelease_path: Optional[str] = None
    plugin_name: Optional[str] = None
    plugin_path: Optional[str] = None
    project_slug: Optional[str] = None
    pylupdate5_path: Optional[str] = None
    repository_url: Optional[str] = None
    transifex_coordinator: Optional[str] = None
    transifex_organization: Optional[str] = None
    transifex_project: Optional[str] = None
    transifex_resource: Optional[str] = None
    translation_source_language: Optional[str] = None
    translation_languages: Optional[str] = None


def touch_file(path, update_time: bool = False, create_dir: bool = True):
    basedir = os.path.dirname(path)
    if create_dir and not os.path.exists(basedir):
        os.makedirs(basedir)
    with open(path, "a"):
        if update_time:
            os.utime(path, None)
        else:
            pass


class Translation:
    def __init__(
        self, parameters: Parameters, transifex_token: str, create_project: bool = True
    ):
        logger.info(f"Overriding test config with: {parameters}")
        client = Transifex(
            api_token=transifex_token,
            organization_name=parameters.transifex_organization,
            i18n_type="QT",
        )
        assert client

        self.tx_client = client
        self.parameters = parameters

        assert self.tx_client.ping()
        plugin_path = self.parameters.plugin_path
        tx = self.parameters.transifex_resource
        lang = self.parameters.translation_source_language
        self.ts_file = f"{plugin_path}/i18n/{tx}_{lang}.ts"

        if self.tx_client.project_exists(parameters.project_slug):
            logger.debug(
                f"Project {self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project} exists on Transifex"
            )

        elif create_project:
            logger.debug(
                "Project does not exists on Transifex, creating one as: "
                f"{self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project}"
            )
            self.tx_client.create_project(
                project_slug=self.parameters.project_slug,
                private=False,
                repository_url=self.parameters.repository_url,
                source_language_code=parameters.translation_source_language,
            )
            assert self.tx_client.project_exists(self.parameters.transifex_project)
            self.update_strings()
            logger.debug(
                f"Creating resource in {self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project}/"
                f"{self.parameters.transifex_resource} with {self.ts_file}"
            )
            self.tx_client.create_resource(
                project_slug=self.parameters.project_slug,
                path_to_file=self.ts_file,
                resource_slug=self.parameters.transifex_resource,
            )
            logger.info(
                f"""
                Transifex project {self.parameters.transifex_organization}/
                {self.parameters.transifex_project} and resource ({self.parameters.transifex_resource}) have been created.
            """
            )
        else:
            logger.error(
                "Project does not exists on Transifex: "
                f"{self.parameters.transifex_organization}/"
                f"{self.parameters.transifex_project}"
            )

    def update_strings(self):
        """
        Update TS files from plugin source strings
        """
        source_py_files = []
        source_ui_files = []
        relative_path = f"./{self.parameters.plugin_path}"
        for ext in ("py", "ui"):
            for file in glob.glob(
                f"{self.parameters.plugin_path}/**/*.{ext}",
                recursive=True,
            ):
                file_path = str(Path(file).relative_to(relative_path))
                if ext == "py":
                    source_py_files.append(file_path)
                else:
                    source_ui_files.append(file_path)

        touch_file(self.ts_file)

        project_file = Path(self.parameters.plugin_path).joinpath(
            self.parameters.plugin_name + ".pro"
        )

        with open(project_file, "w") as f:
            source_py_files = " ".join(source_py_files)
            source_ui_files = " ".join(source_ui_files)
            assert f.write("CODECFORTR = UTF-8\n")
            assert f.write(f"SOURCES = {source_py_files}\n")
            assert f.write(f"FORMS = {source_ui_files}\n")
            assert f.write(
                f"TRANSLATIONS = {Path(self.ts_file).relative_to(relative_path)}\n"
            )
            f.flush()
            f.close()

        cmd = [self.parameters.pylupdate5_path, "-noobsolete", str(project_file)]

        output = subprocess.run(cmd, capture_output=True, text=True)

        project_file.unlink()

        if output.returncode != 0:
            logger.error(f"Translation failed: {output.stderr}")
            sys.exit(1)
        else:
            logger.info(f"Successfully run pylupdate5: {output.stdout}")

    def compile_strings(self):
        """
        Compile TS file into QM files
        """
        cmd = [self.parameters.lrelease_path]
        for file in glob.glob(f"{self.parameters.plugin_path}/i18n/*.ts"):
            cmd.append(file)
        output = subprocess.run(cmd, capture_output=True, text=True)
        if output.returncode != 0:
            logger.error(f"Translation failed: {output.stderr}")
            sys.exit(1)
        else:
            logger.info(f"Successfully run lrelease: {output.stdout}")

    def pull(self):
        """
        Pull TS files from Transifex
        """
        resource = self.__get_resource()
        existing_langs = self.tx_client.list_languages(
            project_slug=self.parameters.project_slug
        )
        lang = self.parameters.translation_source_language
        if lang in existing_langs:
            existing_langs.remove(lang)
        logger.info(
            f"{len(existing_langs)} languages found for resource :"
            f" ({existing_langs})"
        )
        for lang in self.parameters.translation_languages:
            if lang not in existing_langs:
                logger.debug(f"Creating missing language: {lang}")
                self.tx_client.create_language(
                    project_slug=self.parameters.project_slug,
                    language_code=lang,
                    coordinators=[self.parameters.transifex_coordinator],
                )
                existing_langs.append(lang)
        for lang in existing_langs:
            ts_file = f"{self.parameters.plugin_path}/i18n/{self.parameters.transifex_resource}_{lang}.ts"
            logger.debug(f"Downloading translation file: {ts_file}")
            self.tx_client.get_translation(
                project_slug=self.parameters.project_slug,
                resource_slug=resource.slug,
                language_code=lang,
                path_to_output_file=ts_file,
            )

    def push(self):
        resource = self.__get_resource()
        logger.debug(
            f"Pushing resource: {self.parameters.transifex_resource} "
            f"with file {self.ts_file}"
        )
        result = self.tx_client.update_source_translation(
            project_slug=self.parameters.project_slug,
            resource_slug=resource.slug,
            path_to_file=self.ts_file,
        )
        logger.info(f"Translation resource updated: {result}")

    def __get_resource(self) -> dict:
        resources = self.tx_client.list_resources(
            project_slug=self.parameters.project_slug
        )
        if len(resources) == 0:
            logger.error(
                f"Project '{self.parameters.project_slug}' has no resource on Transifex"
            )
            sys.exit(1)
        if len(resources) > 1:
            for resource in resources:
                if resource["name"] == self.parameters.transifex_resource:
                    return resource
            logger.error(
                f"Project '{self.parameters.transifex_project}' has several "
                "resources on Transifex and none is named as the project slug. "
                "Specify one in the parameters with transifex_resource."
                "These resources have been found: "
                f"{', '.join([r['name'] for r in resources])}"
            )
            sys.exit(1)
        return resources[0]
