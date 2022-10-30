from setuptools import setup
import sys

python_min_version = (3, 10)

if sys.version_info < python_min_version:
    sys.exit(
        "pytransifex requires at least Python version {vmaj}.{vmin}.\n"
        "You are currently running this installation with\n\n{curver}".format(
            vmaj=python_min_version[0], vmin=python_min_version[1], curver=sys.version
        )
    )

setup(
    name="pytransifex",
    packages=["pytransifex"],
    version="[VERSION]",
    description="Yet another Python Transifex API.",
    author="Denis Rouzaud",
    author_email="denis.rouzaud@gmail.com",
    url="https://github.com/opengisch/pytransifex",
    download_url="https://github.com/opengisch/pytransifex/archive/[VERSION].tar.gz",  # I'll explain this in a second
    keywords=["Transifex"],
    classifiers=[
        "Topic :: Software Development :: Localization",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Intended Audience :: System Administrators",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=["requests", "click"],
    python_requires=">={vmaj}.{vmin}".format(
        vmaj=python_min_version[0], vmin=python_min_version[1]
    ),
    entry_points={"console_scripts": ["pytx = pytransifex.cli:cli"]},
)
