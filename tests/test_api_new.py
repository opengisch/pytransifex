import unittest
from pathlib import Path

from pytransifex.config import Config
from pytransifex.api_new import Transifex
from pytransifex.interfaces import Tx


def ensure_project(instance):
    if not instance.tx.get_project(project_slug=instance.project_slug):
        instance.tx.create_project(
            project_name=instance.project_name,
            project_slug=instance.project_slug,
            private=True,
        )


class TestNewApi(unittest.TestCase):
    def setUp(self):
        config = Config.from_env()
        self.tx = Transifex(config, defer_login=True)
        self.project_slug = "test_project_pytransifex"
        self.project_name = "Test Project PyTransifex"
        self.resource_slug = "test_resource_fr"
        self.resource_name = "Test Resource FR"
        self.path_to_file = Path(Path.cwd()).joinpath("tests", "test_resource_fr.po")

        if project := self.tx.get_project(project_slug=self.project_slug):
            print("Found a project. Deleting...")
            project.delete()

    def test1_new_api_satisfies_abc(self):
        assert isinstance(self.tx, Tx)

    def test2_create_project(self):
        ensure_project(self)
        assert True

    def test3_list_resources(self):
        ensure_project(self)
        _ = self.tx.list_resources(project_slug=self.project_slug)
        assert True

    def test4_create_resource(self):
        ensure_project(self)
        self.tx.create_resource(
            project_slug=self.project_slug,
            resource_name=self.resource_name,
            resource_slug=self.resource_slug,
            path_to_file=self.path_to_file,
        )
        assert True


"""
    def test5_update_source_translation(self):
        self.update_source_translation(
            project_slug=self.project_slug,
            path_to_file=self.path_to_file,
            resource_slug=self.resource_slug,
        )
        assert True

    def test6_get_translation(self):
        pass

    def test7_list_languages(self):
        languages = self.list_languages(project_slug=self.project_slug)
        assert languages

    def test8_create_language(self):
        pass

    def test9_project_exists(self):
        verdict = self.project_exists(project_slug=self.project_slug)
        assert verdict

    def test10_ping(self):
        pass
"""

if __name__ == "__main__":
    unittest.main()
