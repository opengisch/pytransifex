from distutils.command.upload import upload
from typing import Any
from transifex.api import transifex_api as tx_api
from transifex.api.jsonapi.resources import Resource
from transifex.api.jsonapi import exceptions as json_api_exc

from pytransifex.config import Config
from pytransifex.interfaces import Tx
from pytransifex.utils import ensure_login


class Client(Tx):
    """
    The proper Transifex client expected by the cli and other consumers.
    By default instances are created and logged in 'lazyly' -- when creation or login cannot be deferred any longer.
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

    @ensure_login
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

    @ensure_login
    def get_project(self, project_slug: str) -> None | Resource:
        if projects := self._organization_api_object.fetch("projects"):
            try:
                return projects.get(slug=project_slug)
            except json_api_exc.DoesNotExist:
                return None

    @ensure_login
    def list_resources(self, project_slug: str) -> list[Resource]:
        if projects := self._organization_api_object.fetch("projects"):
            return projects.filter(slug=project_slug)
        raise Exception(
            f"Unable to find any project under this organization: '{self.organization}'"
        )

    @ensure_login
    def create_resource(
        self,
        project_slug: str,
        path_to_file: str,
        resource_slug: str | None = None,
        resource_name: str | None = None,
    ):
        if not (resource_slug or resource_name):
            raise Exception("Please give either a resource_slug or resource_name")

        if project := self.get_project(project_slug=project_slug):
            resource = self.api.Resource.create(
                project=project,
                name=resource_name,
                slug=resource_slug,
                i18n_format=tx_api.I18nFormat(id=self.i18n_type),
            )

            with open(path_to_file, "r") as fh:
                content = fh.read()
                self.api.ResourceStringsAsyncUpload.upload(content, resource=resource)

        else:
            raise Exception(
                f"Not project could be found wiht the slug '{project_slug}'. Please create a project first."
            )

    @ensure_login
    def update_source_translation(
        self, project_slug: str, resource_slug: str, path_to_file: str
    ):
        if resource := self.api.Resource.get(
            slug=resource_slug, project_slug=project_slug
        ):
            with open(path_to_file, "r") as fh:
                content = fh.read()
                self.api.ResourceStringsAsyncUpload(resource, content)
        else:
            raise Exception(
                f"Unable to find resource '{resource_slug}' in project '{project_slug}'"
            )

    @ensure_login
    def get_translation(
        self, project_slug: str, resource_slug: str, language: str, path_to_file: str
    ):
        pass

    @ensure_login
    def list_languages(self, project_slug: str) -> list[Any]:
        if projects := self._organization_api_object.fetch("projects"):
            if project := projects.get(slug=project_slug):
                return project.fetch("languages")
            raise Exception(
                f"Unable to find any project with this slug: '{project_slug}'"
            )
        raise Exception(
            f"Unable to find any project under this organization: '{self.organization}'"
        )

    @ensure_login
    def create_language(self, project_slug: str, path_to_file: str, resource_slug: str):
        pass

    @ensure_login
    def project_exists(self, project_slug: str) -> bool:
        if projects := self._organization_api_object.fetch("projects"):
            if projects.get(slug=project_slug):
                return True
            return False
        raise Exception(
            f"No project could be found under this organization: '{self.organization}'"
        )

    @ensure_login
    def ping(self):
        pass


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
