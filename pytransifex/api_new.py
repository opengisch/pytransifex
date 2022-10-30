from typing import Any
from transifex.api import transifex_api as tx_api
from transifex.api.jsonapi.resources import Resource

from pytransifex.config import Config
from pytransifex.interfaces import Tx
from pytransifex.utils import ensure_logged_client


class Client(Tx):
    """
    The proper Transifex client expecte by the cli and other consumers.
    By default instances are created and logged in 'lazyly' -- when creation and login cannot be deferred any longer.
    Methods defined as "..." are left for further discussion; they are not used anywhere in qgis-plugin-cli.
    """

    def __init__(self, config: Config, defer_login: bool = False):
        """Extract config values, consumes API token against SDK client"""
        self.api_token = config.api_token
        self.host = config.host
        self.organization = config.organization
        self.i18n_type = config.i18n_type
        self.logged_in = False
        self.api = tx_api

        if not defer_login:
            self.login()

    def login(self):
        if self.logged_in:
            return

        self.api.setup(host=self.host, auth=self.api_token)
        self._organization_api_object = self.api.Organization.get(
            slug=self.organization
        )
        self.logged_in = True

    @ensure_logged_client
    def create_project(
        self,
        project_slug: str,
        project_name: str | None = None,
        source_language_code: str = "en_GB",
        private: bool = False,
        *args,
        **kwargs,
    ) -> Resource:
        """Create a project. args, kwargs are there to absorb unnecessary arguments from consumers."""
        source_language = self.api.Language.get(code=source_language_code)
        organization = self._organization_api_object

        return self.api.Project.create(
            name=project_name,
            slug=project_slug,
            source_language=source_language,
            private=private,
            organization=organization,
        )

    @ensure_logged_client
    def get_project(self, project_slug: str) -> Resource:
        if projects := self._organization_api_object.fetch("projects"):
            return projects.get(slug=project_slug)
        raise Exception(f"Project not found: {project_slug}")

    @ensure_logged_client
    def list_resources(self, project_slug: str) -> list[Any]:
        if projects := self._organization_api_object.fetch("projects"):
            return projects.filter(slug=project_slug)
        raise Exception(f"Project not found {project_slug}")

    @ensure_logged_client
    def create_resource(
        self,
        project_slug: str,
        path_to_file: str,
        resource_slug: str | None = None,
        resource_name: str | None = None,
    ):
        if not (resource_slug or resource_name):
            raise Exception("Please give either a resource_slug or resource_name")

        resource = self.api.Resource.create(name=resource_name, slug=resource_slug)
        resource.save(project=project_slug)

        file_handler = open(path_to_file, "r")
        content = file_handler.read()
        file_handler.close()

        self.api.ResourceStringsAsyncUpload.upload(resource, content)

    @ensure_logged_client
    def update_source_translation(
        self, project_slug: str, resource_slug: str, path_to_file: str
    ):
        resource = self.api.Resource.get(slug=resource_slug, project_slug=project_slug)
        file_handler = open(path_to_file, "r")
        content = file_handler.read()
        file_handler.close()
        self.api.ResourceStringsAsyncUpload(resource, content)

    @ensure_logged_client
    def get_translation(
        self, project_slug: str, resource_slug: str, language: str, path_to_file: str
    ):
        ...

    @ensure_logged_client
    def list_languages(self, project_slug: str) -> list[Any]:
        if projects := self._organization_api_object.fetch("projects"):
            if project := projects.get(slug=project_slug):
                return project.fetch("languages")
            raise Exception(f"Unable to find any data for this project {project_slug}")
        raise Exception(
            f"You need at least 1 project to be able to retrieve a list of projects."
        )

    @ensure_logged_client
    def create_language(self, project_slug: str, path_to_file: str, resource_slug: str):
        ...

    @ensure_logged_client
    def project_exists(self, project_slug: str) -> bool:
        if projects := self._organization_api_object.fetch("projects"):
            if projects.get(slug=project_slug):
                return True
            return False
        raise Exception(
            f"No project could be found under this organization: {self.organization}"
        )

    @ensure_logged_client
    def ping(self):
        ...


class Transifex:
    """
    Singleton factory to ensure the client is initialized at most once.
    Simpler to manage than a solution relying on 'imports being imported once in Python.
    """

    client = None

    def __new__(cls, config: Config | None = None, defer_login: bool = False):
        if not cls.client:

            if not config:
                raise Exception("Need to pass config")

            cls.client = Client(config, defer_login)

        return cls.client
