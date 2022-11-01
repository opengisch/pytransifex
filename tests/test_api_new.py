import unittest

from pytransifex.config import Config
from pytransifex.api_new import Transifex
from pytransifex.interfaces import Tx


class TestNewApi(unittest.TestCase):
    def setUp(self):
        config = Config.from_env()
        self.tx = Transifex(config, defer_login=True)
        self.project_slug = "test_project_pytransifex"
        self.project_name = "Test Project PyTransifex"
        self.resource_slug = "test_resource_fr"
        self.resource_name = "Test Resource FR"
        self.path_to_file = "./test_resource_fr.po"

        if project := self.tx.get_project(project_slug=self.project_slug):
            project.delete()

    def test_new_api_satisfies_abc(self):
        assert isinstance(self.tx, Tx)

    def test_create_project(self):
        _ = self.tx.create_project(
            project_name=self.project_name,
            project_slug=self.project_slug,
            private=True,
        )
        assert True

    def test_list_resources(self):
        _ = self.tx.list_resources(project_slug=self.project_slug)
        assert True

    def test_create_resource(self):
        self.tx.create_resource(
            project_slug=self.project_slug,
            resource_name=self.resource_name,
            resource_slug=self.resource_slug,
            path_to_file=self.path_to_file,
        )
        assert True


"""
    def test_update_source_translation(self):
        self.update_source_translation(
            project_slug=self.project_slug,
            path_to_file=self.path_to_file,
            resource_slug=self.resource_slug,
        )
        assert True

    def test_get_translation(self):
        pass

    def test_list_languages(self):
        languages = self.list_languages(project_slug=self.project_slug)
        assert languages

    def test_create_language(self):
        pass

    def test_project_exists(self):
        verdict = self.project_exists(project_slug=self.project_slug)
        assert verdict

    def test_ping(self):
        pass
"""

if __name__ == "__main__":
    unittest.main()
