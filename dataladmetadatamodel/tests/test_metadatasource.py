import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from dataladmetadatamodel import version_string
from dataladmetadatamodel.metadatasource import (
    MetadataSource,
    ImmediateMetadataSource,
    LocalGitMetadataSource
)


class TestFactory(unittest.TestCase):
    def test_immediate_factory(self):
        content_obj = {
            "info": "test-content"
        }
        json_obj = {
            "@": {
                "type": "ImmediateMetadataSource",
                "version": version_string
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
                "version": version_string
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
                "version": version_string
            }
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_unknown_type(self):
        json_obj = {
            "@": {
                "type": "ImmediateMetadataSource",
                "version": version_string
            },
            MetadataSource.TYPE_KEY: "....."
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_faulty_local_git_metadata(self):
        json_obj = {
            "@": {
                "type": "LocalGitMetadataSource",
                "version": version_string
            },
            MetadataSource.TYPE_KEY: LocalGitMetadataSource.TYPE
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_faulty_immediate_metadata(self):
        json_obj = {
            "@": {
                "type": "ImmediateMetadataSource",
                "version": version_string
            },
            MetadataSource.TYPE_KEY: ImmediateMetadataSource.TYPE
        }
        self.assertEqual(MetadataSource.from_json_obj(json_obj), None)

    def test_faulty_class_type(self):
        json_obj = {
            "@": {
                "type": ".....",
                "version": version_string
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


class TestDeepCopy(unittest.TestCase):
    def test_copy_immediate_source(self):
        immediate_metadata = ImmediateMetadataSource("test_content")
        copied_metadata = immediate_metadata.deepcopy()
        self.assertEqual(immediate_metadata, copied_metadata)

    @unittest.skipIf(os.name == "nt", "unix root not handled on windows yet")
    def test_copy_local_git_source(self):
        file_content = "Test file content"
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            object_hash = subprocess.check_output(
                f"echo '{file_content}'|git --git-dir {original_dir}/.git "
                f"hash-object --stdin -w",
                shell=True)

            immediate_source = LocalGitMetadataSource(
                Path(original_dir),
                object_hash.decode().strip())

            copied_object_reference = immediate_source.copy_object_to(
                Path(copy_dir))

            self.assertEqual(
                immediate_source.object_reference,
                copied_object_reference)

            copied_file_content = subprocess.check_output(
                f"git --git-dir {copy_dir}/.git cat-file blob "
                f"{copied_object_reference}",
                shell=True)

            self.assertEqual(
                file_content,
                copied_file_content.decode().strip())


if __name__ == '__main__':
    unittest.main()
