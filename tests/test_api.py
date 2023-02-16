import unittest
from pathlib import Path
from shutil import rmtree

from pytransifex.api import Transifex
from pytransifex.interfaces import Tx


class TestNewApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tx = Transifex(defer_login=True)
        cls.project_slug = "test_project_pytransifex"
        cls.project_name = "Test Project PyTransifex"
        cls.resource_slug = "test_resource_fr"
        cls.resource_name = "Test Resource FR"
        cls.path_to_file = Path.cwd().joinpath("tests", "input", "test_resource_fr.po")
        cls.output_dir = Path.cwd().joinpath("tests", "output")

        if missing := next(filter(lambda p: not p.exists(), [cls.path_to_file]), None):
            raise ValueError(
                f"Unable to complete test with broken tests inputs. Found missing: {missing}"
            )

        if project := cls.tx.get_project(project_slug=cls.project_slug):
            print("Found old project, removing.")
            project.delete()

        print("Creating a brand new project")
        cls.tx.create_project(
            project_name=cls.project_name, project_slug=cls.project_slug, private=True
        )

    @classmethod
    def tearDownClass(cls):
        if Path.exists(cls.output_dir):
            rmtree(cls.output_dir)

    def test1_new_api_satisfies_abc(self):
        assert isinstance(self.tx, Tx)

    def test2_create_project(self):
        # Done in setUpClass
        pass

    def test3_list_resources(self):
        _ = self.tx.list_resources(project_slug=self.project_slug)
        assert True

    def test4_create_resource(self):
        self.tx.create_resource(
            project_slug=self.project_slug,
            resource_name=self.resource_name,
            resource_slug=self.resource_slug,
            path_to_file=self.path_to_file,
        )
        assert True

    def test5_update_source_translation(self):
        self.tx.update_source_translation(
            project_slug=self.project_slug,
            path_to_file=self.path_to_file,
            resource_slug=self.resource_slug,
        )
        assert True

    def test6_create_language(self):
        self.tx.create_language(self.project_slug, "fr_CH")

    def test7_list_languages(self):
        languages = self.tx.list_languages(project_slug=self.project_slug)
        assert languages is not None

    def test8_get_translation(self):
        self.tx.get_translation(
            project_slug=self.project_slug,
            resource_slug=self.resource_slug,
            language_code="fr_CH",
            output_dir=self.output_dir,
        )
        assert Path.exists(Path.joinpath(self.output_dir, self.resource_slug))

    def test9_project_exists(self):
        verdict = self.tx.project_exists(project_slug=self.project_slug)
        assert verdict is not None

    def test10_ping(self):
        self.tx.ping()
        assert True

    def test11_stats(self):
        stats = self.tx.get_project_stats(project_slug=self.project_slug)
        print(str(stats))
        assert stats

    def test12_stats(self):
        self.tx.get_project_stats(project_slug=self.project_slug)

    def test13_stats(self):
        self.tx.get_project_stats(project_slug=self.project_slug)


if __name__ == "__main__":
    unittest.main()

"""
# Don't remove this!
curl -g \
    --request GET --url "https://rest.api.transifex.com/resource_language_stats?filter[project]=o%3Aopengisch%3Ap%3Aqfield-documentation" \
    --header 'accept: application/vnd.api+json' \
    --header 'authorization: Bearer TOKEN'

curl -g \
    --request GET \
    --url "https://rest.api.transifex.com/resource_language_stats?filter[project]=o%3Atest_pytransifex%3Ap%3Atest_project_pytransifex" \
    --header 'accept: application/vnd.api+json' \
    --header 'authorization: Bearer TOKEN'
"""
