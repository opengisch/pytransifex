from types import FunctionType
from typing import Any
from transifex.api import transifex_api as tx_api

from pytransifex.config import Config
from pytransifex.exceptions import PyTransifexException

base_url: str = "https://rest.api.transifex.com"


class TransifexNew:
    # TODO
    # This class satisfies the interface expected by qgis-plugin-cli
    # but it falls short of implementing all the methods defined in
    # pytransifex.api_old.py. The question is whether I should implement them.
    # Is there's a consumer downstream?

    @classmethod
    def get(cls, config: None | Config = None) -> "TransifexNew":
        if cls.transifex:
            return cls.transifex
        if config:
            cls.transifex = cls(config)
            return cls.transifex
        raise PyTransifexException(
            "Need to initialize the program with a working configuration"
        )

    @classmethod
    @property
    def list_funcs(cls) -> list[str]:
        return [n for n, f in cls.__dict__.items() if isinstance(f, FunctionType)]

    def __init__(self, config: Config):
        """Extract config values, consumes API token against SDK client"""
        self.organization = config.organization
        self.i18n_type = config.i18n_type
        self.client = tx_api
        self.client.setup(auth=config.api_token)
        
        """ Set up some state to minimize network round-trips """
        self._organization_api_object = self.client.Organization.get(slug=config.organization)

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

    def list_resources(self, project_slug: str) -> list[Any]:
        if projects := self._organization_api_object.fetch("projects"):
            return projects.filter(slug=project_slug)
        return []

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

    def update_source_translation(
        self, project_slug: str, resource_slug: str, path_to_file: str
    ):
        resource = self.client.Resource.get(slug=slug)

        with open(path_to_file, "r") as handler:
            content = handler.read()
            self.client.ResourceTranslationsAsyncUpload(resource, content)

    def get_translation(
        self, project_slug: str, resource_slug: str, language: str, path_to_file: str
    ):
        ...

    def list_languages(self, project_slug: str, resource_slug: str) -> list[Any]:
        ...

    def create_language(self, project_slug: str, path_to_file: str, resource_slug: str):
        ...

    def project_exists(self, project_slug: str) -> bool:
        if organization := self.client.Organization.get(slug=project_slug):
            if organization.fetch("projects"):
                return True
        return False

    def ping(self):
        ...
