import unittest
from pathlib import Path

from ..metadatasource import MetadataSource, ImmediateMetadataSource,\
    LocalGitMetadataSource


class TestFactory(unittest.TestCase):
    def test_immediate_factory(self):
        content_obj = {
            "info": "test-content"
        }
        json_obj = {
            "@": {
                "type": "ImmediateMetadataSource",
                "version": "1.0"
            },
            MetadataSource.TYPE_KEY: ImmediateMetadataSource.TYPE,
            "content": content_obj
        }
        metadata_object = MetadataSource.from_json_obj(json_obj)
        self.assertIsInstance(metadata_object, ImmediateMetadataSource)
        self.assertEqual(metadata_object.content, content_obj)

    def test_local_git_metadata_factory(self):
        repository_path = Path("/a/b/c/1")
        object_reference = "object-reference-1"
        json_obj = {
            "@": {
                "type": "LocalGitMetadataSource",
                "version": "1.0"
            },
            MetadataSource.TYPE_KEY: LocalGitMetadataSource.TYPE,
            "git_repository_path": repository_path,
            "object_reference": object_reference
        }
        metadata_object = MetadataSource.from_json_obj(json_obj)
        self.assertIsInstance(metadata_object, LocalGitMetadataSource)
        self.assertEqual(metadata_object.git_repository_path, repository_path)
        self.assertEqual(metadata_object.object_reference, object_reference)

    def test_immediate_round_trip(self):
        content = {"test": "test-content-2"}
        immediate_metadata = ImmediateMetadataSource(content)
        created_object = MetadataSource.from_json_obj(
            immediate_metadata.to_json_obj())
        self.assertEqual(immediate_metadata, created_object)

    def test_local_git_metadata_round_trip(self):
        repository_path = Path("/a/b/c/2")
        object_reference = "object-reference-2"
        local_git_metadata = LocalGitMetadataSource(
            repository_path,
            object_reference)
        created_object = MetadataSource.from_json_obj(
            local_git_metadata.to_json_obj())
        self.assertEqual(local_git_metadata, created_object)


class TestFactoryFails(unittest.TestCase):
    def test_missing_type(self):
        json_obj = {
            "@": {
                "type": "ImmediateMetadataSource",
                "version": "1.0"
            }
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_unknown_type(self):
        json_obj = {
            "@": {
                "type": "ImmediateMetadataSource",
                "version": "1.0"
            },
            MetadataSource.TYPE_KEY: "....."
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_faulty_local_git_metadata(self):
        json_obj = {
            "@": {
                "type": "LocalGitMetadataSource",
                "version": "1.0"
            },
            MetadataSource.TYPE_KEY: LocalGitMetadataSource.TYPE
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_faulty_immediate_metadata(self):
        json_obj = {
            "@": {
                "type": "ImmediateMetadataSource",
                "version": "1.0"
            },
            MetadataSource.TYPE_KEY: ImmediateMetadataSource.TYPE
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_faulty_local_git_metadata(self):
        json_obj = {
            "@": {
                "type": "LocalGitMetadataSource",
                "version": "1.0"
            },
            MetadataSource.TYPE_KEY: LocalGitMetadataSource.TYPE
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_faulty_class_type(self):
        json_obj = {
            "@": {
                "type": ".....",
                "version": "1.0"
            }
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_faulty_class_version(self):
        json_obj = {
            "@": {
                "type": "LocalGitMetadataSource",
                "version": "..."
            }
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)


if __name__ == '__main__':
    unittest.main()
