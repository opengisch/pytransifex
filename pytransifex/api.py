import logging
from pathlib import Path
from typing import Any, Optional

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
    Methods with more than 2 parameters don't allow for positional arguments.
    '**kwargs' is used in methods that may need to forward extra named arguments to the API.
    """

    def __init__(self, config: ApiConfig, defer_login=False, reset=False):
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
        logging.info(f"Logged in as organization: {self.organization_name}")

    @ensure_login
    def create_project(
        self,
        *,
        project_slug: str,
        project_name: str | None = None,
        source_language_code: str = "en_GB",
        private: bool = False,
        **kwargs,
    ) -> None | Resource:
        """Create a project."""
        source_language = tx_api.Language.get(code=source_language_code)
        project_name = project_name or project_slug

        try:
            proj = tx_api.Project.create(
                name=project_name,
                slug=project_slug,
                source_language=source_language,
                private=private,
                organization=self.organization,
                **kwargs,
            )
            logging.info(f"Project created with name '{project_name}' !")
            return proj

        except JsonApiException as error:
            if hasattr(error, "detail") and "already exists" in error.detail:  # type: ignore
                return self.get_project(project_slug=project_slug)
            else:
                logging.error(f"Unable to create project; API replied with {error}")

    @ensure_login
    def delete_project(self, project_slug: str):
        if project := self.get_project(project_slug=project_slug):
            project.delete()
            logging.info(f"Deleted project: {project_slug}")

    @ensure_login
    def get_project(self, project_slug: str) -> None | Resource:
        """Fetches the project matching the given slug"""
        if self.projects:
            try:
                res = self.projects.get(slug=project_slug)
                logging.info("Got the project!")
                return res
            except DoesNotExist:
                return None

    @ensure_login
    def list_resources(self, project_slug: str) -> list[Any]:
        """List all resources for the project passed as argument"""
        if project := self.get_project(project_slug=project_slug):
            if resources := project.fetch("resources"):
                return list(resources.all())
            else:
                return []

        raise ValueError(
            f"Unable to find any project under this organization: '{self.organization}'"
        )

    @ensure_login
    def create_resource(
        self,
        *,
        project_slug: str,
        path_to_file: str,
        resource_slug: str | None = None,
        resource_name: str | None = None,
        **kwargs,
    ):
        """Create a resource using the given file contents, slugs and names"""
        if not (resource_slug or resource_name):
            raise ValueError("Please give either a resource_slug or a resource_name")

        if project := self.get_project(project_slug=project_slug):
            resource = tx_api.Resource.create(
                project=project,
                name=resource_name or resource_slug,
                slug=resource_slug or resource_name,
                i18n_format=tx_api.I18nFormat(id=self.i18n_type),
                **kwargs,
            )

            with open(path_to_file, "r") as fh:
                content = fh.read()

            tx_api.ResourceStringsAsyncUpload.upload(content, resource=resource)
            logging.info(f"Resource created: {resource_slug or resource_name}")

        else:
            raise ValueError(
                f"Not project could be found wiht the slug '{project_slug}'. Please create a project first."
            )

    @ensure_login
    def update_source_translation(
        self, project_slug: str, resource_slug: str, path_to_file: str
    ):
        """
        Update the translation strings for the given resource using the content of the file
        passsed as argument
        """
        if not "slug" in self.organization.attributes:
            raise ValueError(
                "Unable to fetch resource for this organization; define an 'organization slug' first."
            )

        logging.info(
            f"Updating source translation for resource {resource_slug} from file {path_to_file} (project: {project_slug})."
        )

        if project := self.get_project(project_slug=project_slug):
            if resources := project.fetch("resources"):
                if resource := resources.get(slug=resource_slug):
                    with open(path_to_file, "r") as fh:
                        content = fh.read()

                    tx_api.ResourceStringsAsyncUpload.upload(content, resource=resource)
                    logging.info(f"Source updated for resource: {resource_slug}")
                    return

        raise ValueError(
            f"Unable to find resource '{resource_slug}' in project '{project_slug}'"
        )

    @ensure_login
    def get_translation(
        self,
        project_slug: str,
        resource_slug: str,
        language_code: str,
        path_to_output_file: None | str = None,
        path_to_output_dir: None | str = None,
    ) -> str:
        """Fetch the translation resource matching the given language"""
        if path_to_output_dir and not path_to_output_file:
            path_to_parent = Path(path_to_output_dir)
            path_to_output_file = str(
                path_to_parent.joinpath(f"{resource_slug}_{language_code}")
            )
        elif path_to_output_file and not path_to_output_dir:
            path_to_parent = Path(path_to_output_file).parent
        else:
            raise ValueError(
                f"get_translation needs exactly one between 'path_to_output_file' (str) or 'path_to_output_dir (str)'. "
            )

        Path.mkdir(path_to_parent, parents=True, exist_ok=True)
        language = tx_api.Language.get(code=language_code)

        if project := self.get_project(project_slug=project_slug):
            if resources := project.fetch("resources"):
                if resource := resources.get(slug=resource_slug):
                    url = tx_api.ResourceTranslationsAsyncDownload.download(
                        resource=resource, language=language
                    )
                    translated_content = requests.get(url).text
                    with open(path_to_output_file, "w") as fh:
                        fh.write(translated_content)

                    logging.info(
                        f"Translations downloaded and written to file (resource: {resource_slug})"
                    )
                    return str(path_to_output_file)

                else:
                    raise ValueError(
                        f"Unable to find any resource with this slug: '{resource_slug}'"
                    )
            else:
                raise ValueError(
                    f"Unable to find any resource for this project: '{project_slug}'"
                )
        else:
            raise ValueError(
                f"Couldn't find any project with this slug: '{project_slug}'"
            )

    @ensure_login
    def list_languages(self, project_slug: str, resource_slug: str) -> list[str]:
        """
        List languages for which there exist translations under the given resource.
        """
        if self.projects:
            if project := self.projects.get(slug=project_slug):
                if resource := project.fetch("resources").get(slug=resource_slug):
                    it = tx_api.ResourceLanguageStats.filter(
                        project=project, resource=resource
                    ).all()

                    language_codes = []
                    for tr in it:
                        """
                        FIXME
                        This is hideous and probably unsound for some language_codes.
                        Couldn't find a more direct accessor to language codes.
                        """
                        code = str(tr).rsplit("_", 1)[-1][:-1]
                        language_codes.append(code)

                    logging.info(f"Obtained these languages: {language_codes}")
                    return language_codes

                raise ValueError(
                    f"Unable to find any resource with this slug: '{resource_slug}'"
                )
            raise ValueError(
                f"Unable to find any project with this slug: '{project_slug}'"
            )
        raise ValueError(
            f"Unable to find any project under this organization: '{self.organization}'"
        )

    @ensure_login
    def create_language(
        self,
        *,
        project_slug: str,
        language_code: str,
        coordinators: None | list[str] = None,
    ):
        """Create a new language resource in the remote Transifex repository"""
        if project := self.get_project(project_slug=project_slug):
            project.add("languages", [tx_api.Language.get(code=language_code)])

            if coordinators:
                project.add("coordinators", coordinators)

            logging.info(
                f"Created language resource for {language_code} and added these coordinators: {coordinators}"
            )

    @ensure_login
    def project_exists(self, project_slug: str) -> bool:
        """Check if the project exists in the remote Transifex repository"""
        try:
            if not self.projects:
                return False
            elif self.projects.get(slug=project_slug):
                return True
            else:
                return False
        except DoesNotExist:
            return False

    @ensure_login
    def ping(self) -> bool:
        """
        Exposing this just for the sake of satisfying qgis-plugin-cli's expectations
        There is no need to ping the server on the current implementation, as connection is handled by the SDK
        """
        logging.info("'ping' is deprecated!")
        return True

    @ensure_login
    def get_project_stats(self, project_slug: str) -> dict[str, Any]:
        if self.projects:
            if project := self.projects.get(slug=project_slug):
                if resource_stats := tx_api.ResourceLanguageStats(project=project):
                    return resource_stats.to_dict()

        raise ValueError(f"Unable to find translation for this project {project_slug}")

    @ensure_login
    def pull(
        self,
        *,
        project_slug: str,
        resource_slugs: list[str],
        language_codes: list[str],
        path_to_output_dir: str,
    ):
        """Pull resources from project."""
        args = []
        for l_code in language_codes:
            for slug in resource_slugs:
                args.append(tuple([project_slug, slug, l_code, path_to_output_dir]))

        res = concurrently(
            fn=self.get_translation,
            args=args,
        )

        logging.info(f"Pulled {args} for {len(res)} results).")

    @ensure_login
    def push(
        self, *, project_slug: str, resource_slugs: list[str], path_to_files: list[str]
    ):
        """Push resources with files under project."""
        if len(resource_slugs) != len(path_to_files):
            raise ValueError(
                f"Resources slugs ({len(resource_slugs)}) and path to files ({len(path_to_files)}) must be equal in size!"
            )

        resource_zipped_with_path = list(zip(resource_slugs, path_to_files))
        resources = self.list_resources(project_slug)
        logging.info(
            f"Found {len(resources)} resource(s) for {project_slug}. Checking for missing resources and creating where necessary."
        )
        created_when_missing_resource = []

        for slug, path in resource_zipped_with_path:
            logging.info(f"Slug: {slug}. Resources: {resources}.")
            if not slug in resources:
                logging.info(
                    f"{project_slug} is missing {slug}. Creating it from {path}."
                )
                self.create_resource(
                    project_slug=project_slug, path_to_file=path, resource_slug=slug
                )
                created_when_missing_resource.append(slug)

        args = [
            tuple([project_slug, slug, path])
            for slug, path in resource_zipped_with_path
            if not slug in created_when_missing_resource
        ]

        res = concurrently(
            fn=self.update_source_translation,
            args=args,
        )

        logging.info(f"Pushed {args} for {len(res)} results.")


class Transifex:
    """
    Singleton factory to ensure the client is initialized at most once.
    Simpler to manage than a solution relying on 'imports being imported once in Python.
    """

    client = None

    def __new__(cls, *, defer_login: bool = False, **kwargs) -> Optional["Client"]:
        if not cls.client:
            try:
                if kwargs:
                    config = ApiConfig(**kwargs)
                else:
                    logging.info(
                        f"As you called 'Transifex' without argument, we'll try defining your project from environment variables."
                    )
                    config = ApiConfig.from_env()

                return Client(config, defer_login)

            except ValueError as error:
                available = list(ApiConfig._fields)
                msg = f"Unable to define a proper config. API initialization uses the following fields, with only 'project_slug' optional: {available}"
                logging.error(f"{msg}:\n{error}")
