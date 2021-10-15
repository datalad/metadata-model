import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.tests.utils import (
    get_location,
    get_uuid,
    assert_dataset_trees_equal,
    create_dataset_tree
)


file_test_paths = [
    MetadataPath("a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x")]

dataset_test_paths = [
    MetadataPath("d1"),
    MetadataPath("d1/d1.1"),
    MetadataPath("d2"),
    MetadataPath("d2/d2.1/d2.1.1"),
    MetadataPath("d3/d3.1")]


uuid_0 = get_uuid(0)


class TestDatasetTree(unittest.TestCase):
    def test_add_metadata(self):

        paths = [
            MetadataPath("a/b/c"),
            MetadataPath("a/b/a"),
            MetadataPath("b"),
            MetadataPath("c/d/e")]

        mrr = MetadataRootRecord(uuid_0, "00112233", None, None)
        dataset_tree = create_dataset_tree(
            dataset_tree_paths=paths,
            initial_mrr=mrr)

        returned_entries = tuple(dataset_tree.get_dataset_paths())

        returned_paths = [entry[0] for entry in returned_entries]
        self.assertEqual(sorted(paths), sorted(returned_paths))

        for entry in returned_entries:
            self.assertEqual(entry[1], mrr)

    def test_root_node(self):

        dataset_tree = DatasetTree()

        mrr = MetadataRootRecord(uuid_0, "00112233", None, None)
        dataset_tree.add_dataset(MetadataPath(""), mrr)
        self.assertEqual(dataset_tree.get_metadata_root_record(MetadataPath("")), mrr)

        returned_entries = tuple(dataset_tree.get_dataset_paths())
        self.assertEqual(len(returned_entries), 1)

        self.assertEqual(returned_entries[0][0], MetadataPath(""))
        self.assertEqual(returned_entries[0][1], mrr)


class TestReferenceCreation(unittest.TestCase):
    def test_object_reference_creation(self):

        dataset_tree = create_dataset_tree(dataset_test_paths)
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

            dataset_tree.write_out("/tmp/t1")

            # We expect one call for the dataset-tree itself
            # and one call for each file-tree, one of which
            # is anchored at each dataset path
            self.assertEqual(
                add_tree_ref.call_count,
                1 + len(dataset_test_paths)
            )


class TestDeepCopy(unittest.TestCase):

    def test_copy_from_memory(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            dataset_tree = create_dataset_tree(dataset_test_paths,
                                               file_test_paths)

            dataset_tree_copy = dataset_tree.deepcopy("git", copy_dir)
            dataset_tree_copy.read_in()

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

            dataset_tree = create_dataset_tree(dataset_test_paths,
                                               file_test_paths)

            dataset_tree.write_out(original_dir)

            dataset_tree_copy = dataset_tree.deepcopy("git", copy_dir)
            dataset_tree_copy.read_in()

            assert_dataset_trees_equal(
                self,
                dataset_tree,
                dataset_tree_copy,
                True)


class TestSubTreeManipulation(unittest.TestCase):

    def get_mrr(self, n: int = 0) -> MetadataRootRecord:
        return MetadataRootRecord(uuid_0, f"00112233-{n}", None, None)

    def test_subtree_adding(self):
        mrr_1 = self.get_mrr(1)
        mrr_2 = self.get_mrr(2)

        tree = DatasetTree()
        tree.add_dataset(MetadataPath("a/b/c"), mrr_1)

        subtree = DatasetTree()
        subtree.add_dataset(MetadataPath("d/e/f"), mrr_2)

        tree.add_subtree(subtree, MetadataPath("a/x"))

        mrr = tree.get_metadata_root_record(MetadataPath("a/b/c"))
        self.assertEqual(mrr, mrr_1)

        mrr = tree.get_metadata_root_record(MetadataPath("a/x/d/e/f"))
        self.assertEqual(mrr, mrr_2)

    def test_subtree_adding_with_conversion(self):
        mrr_1 = self.get_mrr()
        mrr_2 = self.get_mrr()

        tree = DatasetTree()
        tree.add_dataset(MetadataPath("a/b/c"), mrr_1)

        subtree = DatasetTree()
        subtree.add_dataset(MetadataPath("e/f"), mrr_2)

        tree.add_subtree(subtree, MetadataPath("a/b/c/d"))

        node = tree.get_metadata_root_record(MetadataPath("a/b/c"))
        self.assertEqual(node, mrr_1)

        node = tree.get_metadata_root_record(MetadataPath("a/b/c/d/e/f"))
        self.assertEqual(node, mrr_2)

    def test_subtree_adding_on_existing_path(self):
        tree = DatasetTree()
        tree.add_dataset(MetadataPath("a/b/c/d"), self.get_mrr())

        subtree = DatasetTree()
        subtree.add_dataset(MetadataPath("e/f"), self.get_mrr())

        self.assertRaises(
            ValueError,
            tree.add_subtree,
            subtree, MetadataPath("a/b/c/d"))

    def test_subtree_deletion(self):
        mrr_1 = self.get_mrr()
        mrr_2 = self.get_mrr()

        tree = DatasetTree()
        tree.add_dataset(MetadataPath("a/b/c"), mrr_1)
        tree.add_dataset(MetadataPath("a/b/c/d/e/f"), mrr_2)

        self.assertIsNotNone(tree.get_metadata_root_record(MetadataPath("a/b/c/d/e/f")))
        tree.delete_subtree(MetadataPath("a/b/c/d/e/f"))
        self.assertIsNone(tree.get_metadata_root_record(MetadataPath("a/b/c/d/e/f")))
        self.assertIsNotNone(tree.mtree.get_object_at_path(MetadataPath("a/b/c/d/e")))

        tree.delete_subtree(MetadataPath("a/b/c"))
        self.assertIsNotNone(tree.mtree.get_object_at_path(MetadataPath("a/b")))
        self.assertIsNone(tree.get_metadata_root_record(MetadataPath("a/b/c")))
        self.assertIsNone(tree.get_metadata_root_record(MetadataPath("a/b/c/d")))
        self.assertIsNone(tree.get_metadata_root_record(MetadataPath("a/b/c/d/e")))


if __name__ == '__main__':
    unittest.main()
