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

    def test4_create_config(self):
        imported = PluginManager.imported_modules["opengis-mkdocs"]
        config_class = imported.TxProjectConfig
        create_config = imported.create_tx_config
        assert create_config.__name__ == "create_tx_config"
        assert all(hasattr(config_class, k) for k in ["TX_ORGANIZATION", "TX_PROJECT", "TX_SOURCE_LANG", "TX_TYPE"])
        