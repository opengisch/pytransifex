from os import environ
from typing import NamedTuple
from pytransifex.exceptions import PyTransifexException


class Config(NamedTuple):
    api_token: str
    organization: str
    i18n_type: str

    @classmethod
    def from_env(cls) -> "Config":
        token = environ.get("TX_API_TOKEN")
        organization = environ.get("ORGANIZATION")
        i18n_type = environ.get("I18N_TYPE", "PO")

        if any(v is None for v in [token, organization]):
            raise PyTransifexException(
                "Both 'TX_API_TOKEN' and 'ORGANIZATION' must be set environment variables. Aborting now."
            )

        return cls(token, organization, i18n_type)  # type: ignore
