from types import FunctionType
from typing import Any
from transifex.api import transifex_api as tx_api

from pytransifex.config import Config
from pytransifex.exceptions import PyTransifexException
from pytransifex.interfaces import IsTranslator
from pytransifex.utils import auth_client

base_url: str = "https://rest.api.transifex.com"


class Client(IsTranslator):
    @classmethod
    @property
    def list_funcs(cls) -> list[str]:
        return [n for n, f in cls.__dict__.items() if isinstance(f, FunctionType)]

    def __init__(self, config: Config, defer_login: bool = False):
        """Extract config values, consumes API token against SDK client"""
        self.api_token = config.api_token
        self.organization = config.organization
        self.i18n_type = config.i18n_type
        self.client = tx_api
        self.logged_in = False

        if not defer_login:
            self.login()

    def login(self):
        self.client.setup(auth=self.api_token)
        self._organization_api_object = self.client.Organization.get(
            slug=self.organization
        )
        self.logged_in = True

    @auth_client
    def exec(self, fn_name: str, args: dict[str, Any]) -> Any:
        """Adapter for this class to be used from the CLI module"""
        error = ""

        if not fn_name in self.list_funcs:
            defined = "\n".join(self.list_funcs)
            error += f"This function {fn_name} is not defined. Defined are {defined}"

        if "dry_run" in args and args["dry_run"]:
            return error or f"Dry run: Would be calling {fn_name} with {args}."

        if error:
            raise PyTransifexException(error)

        try:
            return getattr(self, fn_name)(**args)
        except Exception as error:
            return str(error)

    @auth_client
    def create_project(
        self,
        project_slug: str,
        project_name: str | None = None,
        source_language_code: str = "en-gb",
        # FIXME: Not sure it's possible to use this param with the new API
        outsource_project_name: str | None = None,
        private: bool = False,
        repository_url: str | None = None,
    ):
        _ = self.client.Project.create(
            name=project_name,
            slug=project_slug,
            private=private,
            organization=self.organization,
            source_language=source_language_code,
            repository_url=repository_url,
        )

    @auth_client
    def list_resources(self, project_slug: str) -> list[Any]:
        if projects := self._organization_api_object.fetch("projects"):
            return projects.filter(slug=project_slug)
        return []

    @auth_client
    def create_resource(
        self,
        # FIXME
        # Unused
        project_slug: str,
        path_to_file: str,
        resource_slug: str | None = None,
        resource_name: str | None = None,
    ):
        # FIXME How to name a to-be-created resource if both resource_slug and resource_name are None?
        slug = resource_slug or resource_name
        resource = self.client.Resource.get(slug=slug)

        if not slug:
            raise PyTransifexException(
                "Please give either a resource_slug or resource_name"
            )

        if not resource:
            raise PyTransifexException(
                f"Unable to find any resource associated with {slug}"
            )

        with open(path_to_file, "r") as handler:
            content = handler.read()
            # self.client.Resource.create(...)
            self.client.ResourceStringsAsyncUpload.upload(resource, content)

    @auth_client
    def update_source_translation(
        self, project_slug: str, resource_slug: str, path_to_file: str
    ):
        resource = self.client.Resource.get(slug=resource_slug)

        with open(path_to_file, "r") as handler:
            content = handler.read()
            self.client.ResourceTranslationsAsyncUpload(resource, content)

    @auth_client
    def get_translation(
        self, project_slug: str, resource_slug: str, language: str, path_to_file: str
    ):
        ...

    @auth_client
    def list_languages(self, project_slug: str, resource_slug: str) -> list[Any]:
        ...

    @auth_client
    def create_language(self, project_slug: str, path_to_file: str, resource_slug: str):
        ...

    @auth_client
    def project_exists(self, project_slug: str) -> bool:
        if organization := self.client.Organization.get(slug=project_slug):
            if organization.fetch("projects"):
                return True
        return False

    @auth_client
    def ping(self):
        ...


class Transifex:
    client = None

    def __new__(cls, config: Config | None = None, defer_login: bool = False):
        if not cls.client:

            if not config:
                raise Exception("Need to pass config")

            cls.client = Client(config,defer_login)

        return cls.client
