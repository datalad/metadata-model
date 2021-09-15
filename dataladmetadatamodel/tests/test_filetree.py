import subprocess
import tempfile
import unittest
from pathlib import Path

from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
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

    def test_root_node(self):
        file_tree = FileTree()
        metadata_node = Metadata()
        file_tree.add_metadata(MetadataPath(""), metadata_node)

        self.assertEqual(file_tree.value, "aaaaa")
        returned_entries = tuple(file_tree.get_paths_recursive())

        self.assertEqual(len(returned_entries), 1)
        self.assertEqual(returned_entries[0][0], MetadataPath(""))
        self.assertEqual(returned_entries[0][1], "aaaa")


class TestMapping(unittest.TestCase):

    def test_shallow_file_tree_mapping(self):
        # assert that file trees content is not mapped by default
        with tempfile.TemporaryDirectory() as metadata_store:

            subprocess.run(["git", "init", metadata_store])

            paths = [
                MetadataPath(""),
                MetadataPath("a")]

            file_tree = FileTree()
            for path in paths:
                file_tree.add_metadata(path, Metadata())
                file_tree.unget_metadata(path, metadata_store)

            reference = file_tree.write_out(metadata_store)
            flush_object_references(Path(metadata_store))

            new_file_tree = FileTree(reference).read_in()
            self.assertFalse(new_file_tree.child_nodes["a"].value.mapped)


class TestDeepCopy(unittest.TestCase):

    def test_copy_from_memory(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            file_tree = FileTree()
            for path in ["", "/a/b/c/d", "/a/b/d", "/a/x"]:
                file_tree.add_metadata(MetadataPath(path), Metadata())

            file_tree_copy = file_tree.deepcopy()
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

            file_tree = FileTree()
            for path in paths:
                file_tree.add_metadata(path, Metadata())
                file_tree.unget_metadata(path, original_dir)
            file_tree.write_out(original_dir)
            #flush_object_references(Path(original_dir))

            file_tree_copy = file_tree.deepcopy()
            #flush_object_references(Path(copy_dir))

            assert_file_trees_equal(self, file_tree, file_tree_copy, True)


if __name__ == '__main__':
    unittest.main()
