import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from typing import cast
from unittest.mock import patch

from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import (
    ExtractorConfiguration,
    Metadata,
    MetadataInstance,
)
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references
from dataladmetadatamodel.tests.utils import (
    assert_file_trees_equal,
    create_file_tree_with_metadata,
    get_location,
)


default_paths = [
    MetadataPath("/a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x"),
]


class TestFileTree(unittest.TestCase):

    def test_add_metadata(self):

        file_tree = create_file_tree_with_metadata(default_paths, [
            Metadata()
            for _ in default_paths])

        returned_entries = tuple(file_tree.get_paths_recursive())

        returned_paths = [entry[0] for entry in returned_entries]
        self.assertEqual(sorted(default_paths), sorted(returned_paths))

        for returned_path, returned_metadata in [
                (entry[0], entry[1])
                for entry in returned_entries]:
            self.assertEqual(returned_metadata, Metadata())

    def test_add_extractor_run(self):

        file_tree = create_file_tree_with_metadata(default_paths, [
            Metadata()
            for _ in default_paths])

        author_name = "Karl-Test"
        author_email = author_name + "@test.com"
        extractor_name = "test_extractor"
        extractor_configuration = ExtractorConfiguration(
            "extractor_version_1",
            {"key1": "value1"})
        metadata_content = {"key0": "this is metadata"}

        file_tree.add_extractor_run(
            default_paths[0],
            1.2,
            extractor_name,
            author_name,
            author_email,
            extractor_configuration,
            metadata_content)

        metadata = file_tree.get_metadata(default_paths[0])
        self.assertIsNotNone(metadata)

        stored_metadata = metadata.extractor_runs_for_extractor(extractor_name)

        self.assertEqual(
            stored_metadata.parameter_set,
            [extractor_configuration])

        self.assertEqual(
            stored_metadata.instances[0],
            MetadataInstance(
                1.2,
                author_name,
                author_email,
                extractor_configuration,
                metadata_content))


class TestReferenceCreation(unittest.TestCase):
    def test_object_reference_creation(self):

        file_tree = create_file_tree_with_metadata(
            default_paths,
            [
                Metadata()
                for _ in default_paths
            ]
        )

        with \
                patch("dataladmetadatamodel.mapper.gitmapper."
                      "metadatamapper.git_save_str") as save_str, \
                patch("dataladmetadatamodel.mapper.gitmapper."
                      "mtreenodemapper.git_save_tree_node") as save_tree_node, \
                patch("dataladmetadatamodel.mapper.gitmapper."
                      "metadatarootrecordmapper.git_save_json") as save_json, \
                patch("dataladmetadatamodel.mtreeproxy."
                      "add_tree_reference") as add_tree_ref:

            save_str.return_value = get_location(1)
            save_tree_node.return_value = get_location(2)
            save_json.return_value = get_location(3)

            file_tree.write_out("/tmp/t1")

            # We expect one call for the dataset-tree itself
            # and one call for each file-tree, one of which
            # is anchored at each dataset path
            add_tree_ref.assert_called_once()


class TestMapping(unittest.TestCase):

    def test_adding(self):
        # check file tree adding is working
        with tempfile.TemporaryDirectory() as metadata_store:

            subprocess.run(["git", "init", metadata_store])

            file_tree = create_file_tree_with_metadata(
                default_paths,
                [Metadata() for _ in default_paths])
            reference = file_tree.write_out(metadata_store)

            file_tree = cast(FileTree, FileTree(
                realm=metadata_store,
                reference=reference).read_in())

            additional_paths = [MetadataPath(f"x/y.{n}") for n in range(10)]
            for additional_path in additional_paths:
                file_tree.add_metadata(additional_path, Metadata())
            reference = file_tree.write_out()

            file_tree = FileTree(realm=metadata_store, reference=reference).read_in()
            read_paths = [pair[0] for pair in file_tree.get_paths_recursive()]
            for path in default_paths + additional_paths:
                self.assertIn(path, read_paths)

    def test_adding_to_massive_tree(self):
        # check file tree adding is working
        with tempfile.TemporaryDirectory() as metadata_store:

            subprocess.run(["git", "init", metadata_store])

            file_tree = FileTree()

            start_time = time.time()
            for first_part in range(10):
                for second_part in range(10):
                    for third_part in range(10):
                        metadata_path = MetadataPath(f"{first_part:03}/"
                                                     f"{second_part:03}/"
                                                     f"{third_part:03}")
                        file_tree.add_metadata(metadata_path, Metadata())
            initialisation_duration = time.time() - start_time
            print(f"Initialised: {initialisation_duration:4f}")

            start_time = time.time()
            reference = file_tree.write_out(metadata_store)
            write_out_duration = time.time() - start_time
            print(f"Written out: {write_out_duration:4f}")

            start_time = time.time()
            file_tree = FileTree(realm=metadata_store, reference=reference).read_in()
            read_in_duration = time.time() - start_time
            print(f"Read in: {read_in_duration:4f}")

            start_time = time.time()
            file_tree.add_metadata(MetadataPath("5/5/xxx"), Metadata())
            add_duration = time.time() - start_time
            print(f"Added single entry: {add_duration:4f}")

            start_time = time.time()
            file_tree.write_out()
            write_out_2nd_duration = time.time() - start_time
            print(f"Written out single entry: {write_out_2nd_duration:4f}")

    def test_shallow_file_tree_mapping(self):
        # assert that file trees content is not mapped by default
        with tempfile.TemporaryDirectory() as metadata_store:

            subprocess.run(["git", "init", metadata_store])

            paths = [
                MetadataPath("a"),
                MetadataPath("b")]

            file_tree = FileTree()
            for path in paths:
                metadata = Metadata()
                file_tree.add_metadata(path, metadata)
                file_tree.unget_metadata(metadata, metadata_store)

            reference = file_tree.write_out(metadata_store)
            flush_object_references(Path(metadata_store))

            new_file_tree = FileTree(realm=metadata_store, reference=reference).read_in()
            self.assertFalse(new_file_tree.mtree.child_nodes["a"].mapped)


class TestDeepCopy(unittest.TestCase):

    def test_copy_from_memory(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            file_tree = FileTree()
            for path in ["a/b/c/d", "a/b/d", "a/x"]:
                file_tree.add_metadata(
                    MetadataPath(path),
                    Metadata())

            file_tree_copy = file_tree.deepcopy(new_destination=copy_dir)
            assert_file_trees_equal(self, file_tree, file_tree_copy, True)

    def test_copy_from_backend(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            paths = [
                MetadataPath("a/b/c/d"),
                MetadataPath("a/b/d"),
                MetadataPath("a/x")]

            file_tree = FileTree()
            for path in paths:
                metadata = Metadata()
                file_tree.add_metadata(path, metadata)
                file_tree.unget_metadata(metadata, original_dir)
            file_tree.write_out(original_dir)

            file_tree_copy = file_tree.deepcopy(new_destination=copy_dir)
            file_tree_copy.read_in()

            assert_file_trees_equal(self, file_tree, file_tree_copy, True)


if __name__ == '__main__':
    unittest.main()
