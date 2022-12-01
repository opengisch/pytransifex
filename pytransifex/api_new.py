from os import mkdir
from pathlib import Path
from typing import Any

import requests
from transifex.api import transifex_api as tx_api
from transifex.api.jsonapi import JsonApiException
from transifex.api.jsonapi.exceptions import DoesNotExist
from transifex.api.jsonapi.resources import Resource

from pytransifex.config import ApiConfig
from pytransifex.interfaces import Tx
from pytransifex.utils import concurrently, ensure_login


class Client(Tx):
    """
    The proper Transifex client expected by the cli and other consumers.
    By default instances are created and logged in 'lazyly' -- when creation or login cannot be deferred any longer.
    """

    def __init__(self, config: ApiConfig, defer_login: bool = False):
        """Extract config values, consumes API token against SDK client"""
        self.api_token = config.api_token
        self.host = config.host_name
        self.organization_name = config.organization_name
        self.i18n_type = config.i18n_type
        self.logged_in = False

        if not defer_login:
            self.login()

    def login(self):
        if self.logged_in:
            return

        # Authentication
        tx_api.setup(host=self.host, auth=self.api_token)
        self.logged_in = True

        # Saving organization and projects to avoid round-trips
        organization = tx_api.Organization.get(slug=self.organization_name)
        self.projects = organization.fetch("projects")
        self.organization = organization
        print(f"Logged in as organization: {self.organization_name}")

    @ensure_login
    def create_project(
        self,
        project_slug: str,
        project_name: str | None = None,
        source_language_code: str = "en_GB",
        private: bool = False,
        *args,
        **kwargs,
    ) -> None | Resource:
        """Create a project. args, kwargs are there to absorb unnecessary arguments from consumers."""
        source_language = tx_api.Language.get(code=source_language_code)

        try:
            res = tx_api.Project.create(
                name=project_name,
                slug=project_slug,
                source_language=source_language,
                private=private,
                organization=self.organization,
            )
            print("Project created!")
            return res
        except JsonApiException as error:
            if "already exists" in error.detail:
                return self.get_project(project_slug=project_slug)

    @ensure_login
    def get_project(self, project_slug: str) -> None | Resource:
        """Fetches the project matching the given slug"""
        if self.projects:
            try:
                res = self.projects.get(slug=project_slug)
                print("Got the project!")
                return res
            except DoesNotExist:
                return None

    @ensure_login
    def list_resources(self, project_slug: str) -> list[Resource]:
        """List all resources for the project passed as argument"""
        if self.projects:
            res = self.projects.filter(slug=project_slug)
            print("Obtained these resources")
            return res
        raise Exception(
            f"Unable to find any project under this organization: '{self.organization}'"
        )

    @ensure_login
    def create_resource(
        self,
        project_slug: str,
        path_to_file: Path,
        resource_slug: str | None = None,
        resource_name: str | None = None,
    ):
        """Create a resource using the given file contents, slugs and names"""
        if not (resource_slug or resource_name):
            raise Exception("Please give either a resource_slug or resource_name")

        if project := self.get_project(project_slug=project_slug):
            resource = tx_api.Resource.create(
                project=project,
                name=resource_name,
                slug=resource_slug,
                i18n_format=tx_api.I18nFormat(id=self.i18n_type),
            )

            with open(path_to_file, "r") as fh:
                content = fh.read()
                tx_api.ResourceStringsAsyncUpload.upload(content, resource=resource)
                print(f"Resource created: {resource_slug or resource_name}")
        else:
            raise Exception(
                f"Not project could be found wiht the slug '{project_slug}'. Please create a project first."
            )

    @ensure_login
    def update_source_translation(
        self, project_slug: str, resource_slug: str, path_to_file: Path
    ):
        """
        Update the translation strings for the given resource using the content of the file
        passsed as argument
        """
        if not "slug" in self.organization.attributes:
            raise Exception(
                "Unable to fetch resource for this organization; define an 'organization slug' first."
            )

        if project := self.get_project(project_slug=project_slug):
            if resources := project.fetch("resources"):
                if resource := resources.get(slug=resource_slug):
                    with open(path_to_file, "r") as fh:
                        content = fh.read()
                        tx_api.ResourceStringsAsyncUpload.upload(
                            content, resource=resource
                        )
                        print(f"Source updated for resource: {resource_slug}")
                        return

        raise Exception(
            f"Unable to find resource '{resource_slug}' in project '{project_slug}'"
        )

    @ensure_login
    def get_translation(
        self,
        project_slug: str,
        resource_slug: str,
        language_code: str,
        output_dir: Path,
    ):
        """Fetch the translation resource matching the given language"""
        language = tx_api.Language.get(code=language_code)
        file_name = Path.joinpath(output_dir, resource_slug)

        if project := self.get_project(project_slug=project_slug):

            if resources := project.fetch("resources"):

                if resource := resources.get(slug=resource_slug):
                    url = tx_api.ResourceTranslationsAsyncDownload.download(
                        resource=resource, language=language
                    )
                    translated_content = requests.get(url).text

                    if not Path.exists(output_dir):
                        mkdir(output_dir)

                    with open(file_name, "w") as fh:
                        fh.write(translated_content)

                    print(
                        f"Translations downloaded and written to file (resource: {resource_slug})"
                    )

                else:
                    raise Exception(
                        f"Unable to find any resource with this slug: '{resource_slug}'"
                    )
            else:
                raise Exception(
                    f"Unable to find any resource for this project: '{project_slug}'"
                )
        else:
            raise Exception(
                f"Couldn't find any project with this slug: '{project_slug}'"
            )

    @ensure_login
    def list_languages(self, project_slug: str) -> list[Any]:
        """
        List all languages for which there is at least 1 resource registered
        under the parameterised project
        """
        if self.projects:
            if project := self.projects.get(slug=project_slug):
                languages = project.fetch("languages")
                print(f"Obtained these languages")
                return languages
            raise Exception(
                f"Unable to find any project with this slug: '{project_slug}'"
            )
        raise Exception(
            f"Unable to find any project under this organization: '{self.organization}'"
        )

    @ensure_login
    def create_language(
        self,
        project_slug: str,
        language_code: str,
        coordinators: None | list[Any] = None,
    ):
        """Create a new language resource in the remote Transifex repository"""
        if project := self.get_project(project_slug=project_slug):
            project.add("languages", [tx_api.Language.get(code=language_code)])

            if coordinators:
                project.add("coordinators", coordinators)

            print(f"Created language resource for {language_code}")

    @ensure_login
    def project_exists(self, project_slug: str) -> bool:
        """Check if the project exists in the remote Transifex repository"""
        if self.projects:
            if self.projects.get(slug=project_slug):
                return True
            return False
        raise Exception(
            f"No project could be found under this organization: '{self.organization}'"
        )

    @ensure_login
    def ping(self):
        """
        Exposing this just for the sake of satisfying qgis-plugin-cli's expectations
        There is no need to ping the server on the current implementation, as connection is handled by the SDK
        """
        print("'ping' is deprecated!")

    @ensure_login
    def get_project_stats(self, project_slug: str) -> dict[str, Any]:
        if self.projects:
            if project := self.projects.get(slug=project_slug):
                if resource_stats := tx_api.ResourceLanguageStats(project=project):
                    return resource_stats.to_dict()

        raise Exception(f"Unable to find translation for this project {project_slug}")

    @ensure_login
    def pull(
        self,
        project_slug: str,
        resource_slugs: list[str],
        language_codes: list[str],
        output_dir: Path,
    ):
        args = []
        for l_code in language_codes:
            for slug in resource_slugs:
                args.append(tuple([project_slug, slug, l_code, output_dir]))
        print("ARGS", args)
        concurrently(
            fn=self.get_translation,
            args=args,
        )

    @ensure_login
    def push(
        self, project_slug: str, resource_slugs: list[str], path_to_files: list[Path]
    ):
        if len(resource_slugs) != len(path_to_files):
            raise Exception(
                f"Resources slugs ({len(resource_slugs)}) and Path to files ({len(path_to_files)}) must be equal in size!"
            )

        args = [
            tuple([project_slug, res, path])
            for res, path in zip(resource_slugs, path_to_files)
        ]

        concurrently(
            fn=self.update_source_translation,
            args=args,
        )

        print(f"Pushes some {len(resource_slugs)} files!")


class Transifex:
    """
    Singleton factory to ensure the client is initialized at most once.
    Simpler to manage than a solution relying on 'imports being imported once in Python.
    """

    client = None

    def __new__(cls, defer_login: bool = False):
        if not cls.client:
            cls.client = Client(ApiConfig.from_env(), defer_login)
        return cls.client
