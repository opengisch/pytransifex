from dataclasses import asdict, dataclass
from os import environ
from pathlib import Path
from typing import Any, NamedTuple

import toml
from dotenv import load_dotenv


class ApiConfig(NamedTuple):
    api_token: str
    organization_name: str
    i18n_type: str
    host_name = "https://rest.api.transifex.com"
    project_slug: str | None = None

    @classmethod
    def from_env(cls) -> "ApiConfig":
        load_dotenv()

        token = environ.get("TX_TOKEN")
        organization = environ.get("ORGANIZATION")
        i18n_type = environ.get("I18N_TYPE", "PO")

        if faulty := next(
            filter(
                lambda v: not v[1],
                zip(
                    ["token", "organization", "i18_ntype"],
                    [token, organization, i18n_type],
                ),
            ),
            None,
        ):
            raise ValueError(
                f"Envars 'TX_TOKEN', 'ORGANIZATION' and 'I18N_TYPE must be set to non-empty values, yet this one was found missing ('None' or empty string): {faulty[0]}"
            )

        return cls(token, organization, i18n_type)  # type: ignore


path_keys = ["input_directory", "output_directory", "config_file"]
mandatory = ["organization_slug", "project_slug"]
defaults = {
    "output_directory": Path.cwd().joinpath("output"),
    "config_file": Path.cwd().joinpath(".pytx_config.yml"),
}


@dataclass
class CliSettings:
    organization_slug: str
    project_slug: str
    input_directory: Path | None
    output_directory: Path = defaults["output_directory"]
    config_file: Path = defaults["config_file"]

    @classmethod
    def extract_settings(cls, **user_data) -> "CliSettings":
        if missing := [k for k in mandatory if not k in user_data]:
            raise Exception(
                f"These keys are not set or do not have a well-defined value: {', '.join(missing)}"
            )
        if empty := [k for k, v in user_data.items() if k in mandatory and not v]:
            raise Exception(f"These keys have an empty value: {', '.join(empty)}")

        organization_slug = user_data["organization_slug"]
        project_slug = user_data["project_slug"]
        input_directory = user_data.get("input_directory")
        config_file = CliSettings.get_or_default("config_file", user_data)
        output_directory = CliSettings.get_or_default("output_directory", user_data)

        return cls(
            organization_slug,
            project_slug,
            input_directory,
            output_directory,
            config_file,
        )

    @classmethod
    def from_disk(cls) -> "CliSettings":
        d = toml.load(cls.config_file)
        return cls.extract_settings(**d)

    def to_disk(self):
        with open(self.config_file, "w") as fh:
            toml.dump(self.serialize(), fh)

    def serialize(self) -> dict[str, Any]:
        return {
            k: (str(v) if k in path_keys else v)
            for k, v in asdict(self).items()
            if v is not None
        }

    @staticmethod
    def deserialize(d: dict[str, Any]) -> dict[str, Any]:
        return {k: (Path(v) if k in path_keys else v) for k, v in d.items()}

    @staticmethod
    def get_or_default(k: str, obj: dict[str, Any]) -> Any:
        truthy_obj = {k: v for k, v in obj.items() if v}
        if k in truthy_obj:
            return truthy_obj[k]
        return defaults[k]
