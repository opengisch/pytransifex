from abc import ABC, abstractmethod
from typing import Any


class Tx(ABC):
    # TODO
    # This interface modelled after api.py:Transifex satisfies the expectations of qgis-plugin-cli
    # but it falls short of requiring an implementation for methods that qgis-plugin-cli does not use:
    # { coordinator, create_translation, delete_project, delete_resource, delete_team }

    @abstractmethod
    def create_project(
        self,
        project_slug: str,
        project_name: str | None = None,
        source_language_code: str = "en-gb",
        outsource_project_name: str | None = None,
        private: bool = False,
        repository_url: str | None = None,
    ):
        raise NotImplementedError

    def delete_project(self, project_slug: str):
        ...

    @abstractmethod
    def list_resources(self, project_slug: str) -> list[Any]:
        raise NotImplementedError

    def delete_team(self, team_slug: str):
        ...

    @abstractmethod
    def create_resource(
        self,
        project_slug: str,
        path_to_file: str,
        resource_slug: str | None = None,
        resource_name: str | None = None,
    ):
        raise NotImplementedError

    def delete_resource(self, project_slug: str, resource_slug: str):
        ...

    @abstractmethod
    def update_source_translation(
        self, project_slug: str, resource_slug: str, path_to_file: str
    ):
        raise NotImplementedError

    def create_translation(
        self, project_slug: str, language_code: str, path_to_file: str
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_translation(
        self, project_slug: str, resource_slug: str, language: str, path_to_file: str
    ):
        raise NotImplementedError

    @abstractmethod
    def list_languages(self, project_slug: str) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    def create_language(self, project_slug: str, path_to_file: str, resource_slug: str):
        raise NotImplementedError

    def coordinator(self, project_slug: str, language_code="str") -> str:
        ...

    @abstractmethod
    def project_exists(self, project_slug: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def ping(self) -> bool:
        raise NotImplementedError
