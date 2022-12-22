import sys
from functools import reduce
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any


class PluginManager:
    # list of path_to_ subdir, path_to_ main.py
    discovered_subdir_main: list[tuple[Path, Path]] = []
    # successfully imported modules
    imported_modules: dict[str, Any] = {}

    @staticmethod
    def discover():
        """
        Expecting directory structure:
            pytransifex/
                config-plugins/{plugins}
                    main.py
        """
        plugins_dir = Path.cwd().joinpath("pytransifex", "config-plugins")
        subdirs = [f for f in plugins_dir.iterdir() if f.is_dir()]

        def collect_mains(acc: list[Path], sub: Path):
            main = Path(sub).joinpath("main.py")

            if main.exists() and main.is_file():
                acc.append(main)

            return acc

        collected = reduce(collect_mains, subdirs, [])
        PluginManager.discovered_subdir_main = list(zip(subdirs, collected))

    @staticmethod
    def load_plugin(target_plugin_dir: str):
        conventional_main = "main.py"

        if name_main := next(
            (
                (main_p, directory_p.name)
                for directory_p, main_p in PluginManager.discovered_subdir_main
                if directory_p.name == target_plugin_dir
            ),
            None,
        ):
            main, name = name_main

            if name in PluginManager.imported_modules:
                print("Already imported! Nothing to do.")
                return

            if spec := spec_from_file_location(conventional_main, main):
                module = module_from_spec(spec)
                sys.modules[conventional_main] = module

                if spec.loader:
                    spec.loader.exec_module(module)
                    PluginManager.imported_modules[name] = module
                    print(
                        f"Successfully imported and loaded {module}! Imported modules read: {PluginManager.imported_modules}"
                    )

                else:
                    raise Exception(f"Failed to load module '{module}' at {main}")

            else:
                raise Exception(f"Unable to find spec 'main.py' for {main}")

        else:
            raise Exception(
                f"Couldn't find the '{target_plugin_dir}' directory; it was expected to be a child of the 'pytransifex' directory."
            )
