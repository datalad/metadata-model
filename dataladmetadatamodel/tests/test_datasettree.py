import subprocess
import tempfile
import unittest
from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references

from .utils import assert_dataset_trees_equal, create_dataset_tree


file_test_paths = ["", "a/b/c", "a/b/a", "b", "c/d/e", "a/x"]
dataset_test_paths = ["", "d1", "d1/d1.1", "d2", "d2/d2.1/d2.1.1", "d3/d3.1"]


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

            dataset_tree = create_dataset_tree(
                "git",
                original_dir,
                dataset_test_paths,
                file_test_paths)

            dataset_tree_copy = dataset_tree.deepcopy("git", copy_dir)
            flush_object_references(copy_dir)

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

            dataset_tree = create_dataset_tree(
                "git",
                original_dir,
                dataset_test_paths,
                file_test_paths)

            dataset_tree.save()
            flush_object_references(original_dir)

            dataset_tree_copy = dataset_tree.deepcopy("git", copy_dir)
            flush_object_references(copy_dir)

            assert_dataset_trees_equal(
                self,
                dataset_tree,
                dataset_tree_copy,
                False)


class TestSubTreeManipulation(unittest.TestCase):
    def get_mrr(
            self,
            mapper: str,
            realm: str) -> MetadataRootRecord:

        return MetadataRootRecord(
            mapper, realm, uuid_0, "00112233",
            Connector.from_object(None),
            Connector.from_object(None))

    def test_subtree_adding(self):
        mrr_1 = self.get_mrr("memory", "")
        mrr_2 = self.get_mrr("memory", "")

        tree = DatasetTree("memory", "")
        tree.add_dataset("a/b/c", mrr_1)

        subtree = DatasetTree("memory", "")
        subtree.add_dataset("d/e/f", mrr_2)

        tree.add_subtree(subtree, "a/x")

        node = tree.get_node_at_path("a/b/c")
        self.assertIsNotNone(node)
        self.assertEqual(node.value, mrr_1)

        node = tree.get_node_at_path("a/x/d/e/f")
        self.assertIsNotNone(node)
        self.assertEqual(node.value, mrr_2)

    def test_subtree_adding_with_conversion(self):
        mrr_1 = self.get_mrr("memory", "")
        mrr_2 = self.get_mrr("memory", "")

        tree = DatasetTree("memory", "")
        tree.add_dataset("a/b/c", mrr_1)

        subtree = DatasetTree("memory", "")
        subtree.add_dataset("e/f", mrr_2)

        tree.add_subtree(subtree, "a/b/c/d")

        node = tree.get_node_at_path("a/b/c")
        self.assertIsNotNone(node)
        self.assertEqual(node.value, mrr_1)

        node = tree.get_node_at_path("a/b/c/d/e/f")
        self.assertIsNotNone(node)
        self.assertEqual(node.value, mrr_2)

    def test_subtree_adding_on_existing_path(self):
        tree = DatasetTree("memory", "")
        tree.add_dataset("a/b/c/d", self.get_mrr("memory", ""))

        subtree = DatasetTree("memory", "")
        subtree.add_dataset("e/f", self.get_mrr("memory", ""))

        self.assertRaises(
            ValueError,
            tree.add_subtree,
            subtree, "a/b/c/d")

    def test_subtree_deletion(self):
        mrr_1 = self.get_mrr("memory", "")
        mrr_2 = self.get_mrr("memory", "")

        tree = DatasetTree("memory", "")
        tree.add_dataset("a/b/c", mrr_1)
        tree.add_dataset("a/b/c/d/e/f", mrr_2)

        self.assertIsNotNone(tree.get_node_at_path("a/b/c/d/e/f"))
        tree.delete_subtree("a/b/c/d/e/f")
        self.assertIsNone(tree.get_node_at_path("a/b/c/d/e/f"))
        self.assertIsNotNone(tree.get_node_at_path("a/b/c/d/e"))

        self.assertIsNotNone(tree.get_node_at_path("a/b/c/d/e"))
        tree.delete_subtree("a/b/c")
        self.assertIsNotNone(tree.get_node_at_path("a/b"))
        self.assertIsNone(tree.get_node_at_path("a/b/c"))
        self.assertIsNone(tree.get_node_at_path("a/b/c/d"))
        self.assertIsNone(tree.get_node_at_path("a/b/c/d/e"))


if __name__ == '__main__':
    unittest.main()
