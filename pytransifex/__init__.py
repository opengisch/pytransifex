import logging
from sys import version_info

if version_info.major != 3 or version_info.minor < 10:
    raise RuntimeError(
        f"This program requires Python 3.10 at least, but found {version_info.major}.{version_info.minor}"
    )

logging.basicConfig(level=logging.INFO)
