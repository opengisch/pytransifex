# © 2022 Mario Baranzini @ mario.baranzini@opengis.ch
import glob
import logging
import os
from typing import NamedTuple

import frontmatter


class TxProjectConfig(NamedTuple):
    TX_ORGANIZATION = "opengisch"
    TX_PROJECT = "qfield-documentation"
    TX_SOURCE_LANG = "en"
    TX_TYPE = "GITHUBMARKDOWN"


def create_transifex_config(config: TxProjectConfig):
    """Parse all source documentation files and add the ones with tx_slug metadata
    defined to transifex config file.
    """
    logging.info("Start creating transifex configuration")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_dir, "..", ".tx", "config")
    root = os.path.join(current_dir, "..")
    count = 0

    with open(config_file, "w") as f:
        f.write("[main]\n")
        f.write("host = https://www.transifex.com\n\n")

        for file in glob.iglob(
            current_dir + "/../documentation/**/*.en.md", recursive=True
        ):

            # Get relative path of file
            relative_path = os.path.relpath(file, start=root)

            tx_slug = frontmatter.load(file).get("tx_slug", None)

            if tx_slug:
                logging.info(
                    f"Found file with tx_slug defined: {relative_path}, {tx_slug}"
                )
                f.write(
                    f"[o:{config.TX_ORGANIZATION}:p:{config.TX_PROJECT}:r:{tx_slug}]\n"
                )
                f.write(
                    f"file_filter = {''.join(relative_path.split('.')[:-2])}.<lang>.md\n"
                )
                f.write(f"source_file = {relative_path}\n")
                f.write(f"source_lang = {config.TX_SOURCE_LANG}\n")
                f.write(f"type = {config.TX_TYPE}\n\n")
                count += 1

    logging.info(f"Transifex configuration created. {count} resources added.")
