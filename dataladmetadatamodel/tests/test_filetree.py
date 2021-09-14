import subprocess
import tempfile
import unittest
from pathlib import Path

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references

from dataladmetadatamodel.tests.utils import (
    assert_file_trees_equal,
    create_file_tree_with_metadata
)


default_paths = [
    MetadataPath("a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x")
]


class TestFileTree(unittest.TestCase):

    def test_add_metadata(self):

        file_tree = create_file_tree_with_metadata(
            "git",
            "/tmp",
            default_paths,
            [
                Metadata("git", f"/tmp/{p}")
                for p in default_paths
            ])

        returned_entries = tuple(file_tree.get_paths_recursive())

        returned_paths = [entry[0] for entry in returned_entries]
        self.assertEqual(sorted(default_paths), sorted(returned_paths))

        for returned_path, returned_metadata in [
                (entry[0], entry[1].object)
                for entry in returned_entries]:

            self.assertEqual(
                returned_metadata,
                Metadata("git", f"/tmp/{returned_path}"))

    def test_root_node(self):
        from dataladmetadatamodel.mapper.gitmapper.persistedreferenceconnector import PersistedReferenceConnector
        file_tree = FileTree("git", "/tmp")
        metadata_node = Metadata("git", "/tmp")
        file_tree.add_metadata(MetadataPath(""), metadata_node)

        expected_connector = PersistedReferenceConnector.from_object(metadata_node)
        self.assertEqual(file_tree.value, expected_connector)
        returned_entries = tuple(file_tree.get_paths_recursive())

        self.assertEqual(len(returned_entries), 1)
        self.assertEqual(returned_entries[0][0], MetadataPath(""))
        self.assertEqual(returned_entries[0][1], expected_connector)


class TestMapping(unittest.TestCase):

    def test_shallow_file_tree_mapping(self):
        # assert that file trees content is not mapped by default
        with tempfile.TemporaryDirectory() as metadata_store:

            subprocess.run(["git", "init", metadata_store])

            paths = [
                MetadataPath(""),
                MetadataPath("a")]

            file_tree = FileTree("git", metadata_store)
            for path in paths:
                file_tree.add_metadata(path, Metadata("git", metadata_store))
                file_tree.unget_metadata(path)

            reference = file_tree.save()
            flush_object_references(Path(metadata_store))

            new_file_tree = Connector.from_reference(reference).load_object()
            self.assertFalse(new_file_tree.child_nodes["a"].value.is_mapped)


class TestDeepCopy(unittest.TestCase):

    def test_copy_from_memory(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            file_tree = FileTree("git", original_dir)
            file_tree.add_metadata(
                MetadataPath(""),
                Metadata("git", original_dir))
            file_tree.add_metadata(
                MetadataPath("/a/b/c/d"),
                Metadata("git", original_dir))
            file_tree.add_metadata(
                MetadataPath("/a/b/d"),
                Metadata("git", original_dir))
            file_tree.add_metadata(
                MetadataPath("/a/x"),
                Metadata("git", original_dir))

            BaseMapper.start_mapping_cycle()
            file_tree_copy = file_tree.deepcopy("git", copy_dir)

            assert_file_trees_equal(self, file_tree, file_tree_copy, True)

    def test_copy_from_backend(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            paths = [
                MetadataPath(""),
                MetadataPath("a/b/c/d"),
                MetadataPath("a/b/d"),
                MetadataPath("a/x")]

            BaseMapper.start_mapping_cycle()

            file_tree = FileTree("git", original_dir)
            for path in paths:
                file_tree.add_metadata(path, Metadata("git", original_dir))
                file_tree.unget_metadata(path)

            file_tree.save()
            flush_object_references(Path(original_dir))

            file_tree_copy = file_tree.deepcopy("git", copy_dir)
            flush_object_references(Path(copy_dir))

            assert_file_trees_equal(self, file_tree, file_tree_copy, True)


if __name__ == '__main__':
    unittest.main()
