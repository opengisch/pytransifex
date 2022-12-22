import unittest

from pytransifex.plugins_manager import PluginManager


class TestPluginsRegistrar(unittest.TestCase):
    def test1_plugin_discover(self):
        PluginManager.discover()
        assert list(PluginManager.discovered_subdir_main)

    def test2_plugin_import(self):
        PluginManager.load_plugin("opengis-mkdocs")
        assert list(PluginManager.imported_modules)

    def test3_imported_plugin(self):
        assert PluginManager.imported_modules["opengis-mkdocs"].TxProjectConfig
