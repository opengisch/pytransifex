from typing import Any, Protocol, runtime_checkable

from pytransifex.config import Config


@runtime_checkable
class IsTranslator(Protocol):
    @classmethod
    def get(cls, config: None | Config = None):
        ...

    @classmethod
    @property
    def list_funcs(cls) -> list[str]:
        ...

    def exec(self, fn_name: str, args: dict[str, Any]) -> Any:
        ...

    def ping(self):
        ...

    def project_exists(self, project: str) -> bool:
        ...

    def create_project(
        self,
        project_slug: str,
        project_name: str | None = None,
        source_language_code: str = "en-gb",
        outsource_project_name: str | None = None,
        private: bool = False,
        repository_url: str | None = None,
    ):
        ...

    def list_resources(self, project_slug: str) -> list[Any]:
        ...

    def create_resource(
        self,
        project_slug: str,
        path_to_file: str,
        resource_slug: str | None = None,
        resource_name: str | None = None,
    ):
        ...

    def update_source_translation(
        self, project_slug: str, resource_slug: str, path_to_file: str
    ):
        ...

    def get_translation(
        self, project_slug: str, resource_slug: str, language: str, path_to_file: str
    ):
        ...

    def list_languages(self, project_slug: str, resource_slug: str) -> list[Any]:
        ...

    def create_language(self, project_slug: str, path_to_file: str, resource_slug: str):
        ...
