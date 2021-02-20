import subprocess
import tempfile
import unittest
from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references

from .utils import assert_dataset_trees_equal


uuid_0 = UUID("00000000000000000000000000000000")


class TestDatasetTree(unittest.TestCase):
    def test_add_metadata(self):

        paths = ["a/b/c", "a/b/a", "b", "c/d/e"]

        dataset_tree = DatasetTree("git", "/tmp")
        mrr = MetadataRootRecord(
            "git", "/tmp", uuid_0, "00112233",
            Connector.from_object(None),
            Connector.from_object(None)
        )
        for path in paths:
            dataset_tree.add_dataset(path, mrr)

        returned_entries = tuple(dataset_tree.get_dataset_paths())

        returned_paths = [entry[0] for entry in returned_entries]
        self.assertEqual(sorted(paths), sorted(returned_paths))

        for entry in returned_entries:
            self.assertEqual(entry[1], mrr)

    def test_root_node(self):
        dataset_tree = DatasetTree("git", "/tmp")
        mrr = MetadataRootRecord(
            "git", "/tmp", uuid_0, "00112233",
            Connector.from_object(None),
            Connector.from_object(None)
        )
        dataset_tree.add_dataset("", mrr)
        self.assertEqual(dataset_tree.value, mrr)

        returned_entries = tuple(dataset_tree.get_dataset_paths())
        self.assertEqual(len(returned_entries), 1)

        self.assertEqual(returned_entries[0][0], "")
        self.assertEqual(returned_entries[0][1], mrr)


class TestDeepCopy(unittest.TestCase):

    def test_copy_from_memory(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            dataset_tree = DatasetTree("git", original_dir)
            dataset_tree.add_dataset("", MetadataRootRecord("git", original_dir))
            dataset_tree.add_dataset("/a/b/c/d", MetadataRootRecord("git", original_dir))
            dataset_tree.add_dataset("/a/b/d", MetadataRootRecord("git", original_dir))
            dataset_tree.add_dataset("/a/x", MetadataRootRecord("git", original_dir))

            dataset_tree_copy = dataset_tree.deepcopy("git", copy_dir)

            assert_dataset_trees_equal(
                self,
                dataset_tree,
                dataset_tree_copy,
                True)

    def test_copy_from_backend(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            paths = ["", "a/b/c/d", "a/b/d", "a/x"]
            dataset_tree = DatasetTree("git", original_dir)
            for path in paths:
                dataset_tree.add_dataset(path, MetadataRootRecord("git", original_dir))
            dataset_tree.save()
            flush_object_references(original_dir)

            dataset_tree_copy = dataset_tree.deepcopy("git", copy_dir)
            flush_object_references(copy_dir)

            assert_dataset_trees_equal(self, dataset_tree, dataset_tree_copy, False)


if __name__ == '__main__':
    unittest.main()
