from dataclasses import dataclass
from os import environ
from pathlib import Path
from typing import NamedTuple

from dotenv import load_dotenv


class Config(NamedTuple):
    api_token: str
    organization_name: str
    i18n_type: str
    host_name = "https://rest.api.transifex.com"
    project_slug: str | None = None

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()

        token = environ.get("TX_TOKEN")
        organization = environ.get("ORGANIZATION")
        i18n_type = environ.get("I18N_TYPE", "PO")

        if any(not v for v in [token, organization, i18n_type]):
            raise Exception(
                "Envars 'TX_TOKEN' and 'ORGANIZATION' must be set to non-empty values. Aborting now."
            )

        return cls(token, organization, i18n_type)  # type: ignore


@dataclass
class CliSettings:
    organization_slug: str
    project_slug: str | None
    input_directory: Path | None
    output_directory: Path | None
