import logging
from pathlib import Path

import toml

logging.basicConfig(level=logging.INFO)

p = Path.cwd().joinpath("./tests/data/test_config.toml")
test_config = toml.load(p)

logging.info(f"Running tests with this test_config: {test_config}")
