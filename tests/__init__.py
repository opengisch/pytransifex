import logging
from pathlib import Path

import toml

logging.basicConfig(level=logging.INFO)

private = Path.cwd().joinpath("./tests/data/test_config.toml")
test_config = toml.load(private)

public = Path.cwd().joinpath("./tests/data/test_config_public.toml")
test_config_public = toml.load(public)

logging.info(
    f"Running tests with this test_config: {test_config} and test_config_public: {test_config_public}"
)
