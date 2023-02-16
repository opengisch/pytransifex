
### PyTransifex: yet another Python Transifex API

Read the documentation: https://opengisch.github.io/pytransifex

This was largely based on https://github.com/jakul/python-transifex which was not made available for Python 3.

This can be imported as a library or run as a CLI executable (`pytx`). Read on for the latter use case.

### Build the package (required for consuming the package as a CLI)

Ensure that `build` is installed for the current user or project:
- current user: `pip3 --user install build`
- local project: `pipenv install --dev build`

#### 1. Build the installable archive

Build the package:
- current user: `pip3 -m build`
- local project: `pipenv run build`

#### 2. Install from the archive

This will create a `dist` in the current directory, with a `tar.gz` archive in it. You can finally install it:
- current user: `pip3 --user install <path/to/the/archive>`
- local project: `pipenv install <path/to/the/archive>`

#### 3. Run the pytx cli

Once installed the package can be run as a CLI; example:

    pytx pull name -l fr

Run `pytx --help` for more information.
