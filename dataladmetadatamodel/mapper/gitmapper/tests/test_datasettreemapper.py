import subprocess
import unittest
from tempfile import TemporaryDirectory
from typing import List
from uuid import UUID

from ....datasettree import DatasetTree
from ....filetree import FileTree
from ....metadata import Metadata
from ....metadatapath import MetadataPath
from ....metadatarootrecord import MetadataRootRecord
from ....tests.utils import create_dataset_tree


initial_dataset_paths = [
    MetadataPath("a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x")
]

initial_file_paths = [
    MetadataPath(""),
    MetadataPath("a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x")]

uuid_0 = UUID("00000000000000000000000000000000")


class TestDatasetTreeMapper(unittest.TestCase):

    def save_load_compare(self,
                          dataset_tree: DatasetTree,
                          destination: str,
                          expected_paths: List[MetadataPath]) -> DatasetTree:

        reference = dataset_tree.write_out(destination)
        dataset_tree = None

        new_dataset_tree = DatasetTree(reference)
        new_dataset_tree.read_in()
        loaded_paths = [p[0] for p in new_dataset_tree.get_paths_recursive()]

        self.assertEqual(len(loaded_paths), len(expected_paths))
        self.assertTrue(all(map(lambda np: np in expected_paths, loaded_paths)))
        return new_dataset_tree

    # Ensure that updates do not destroy existing git-trees
    def test_load_update_write(self):
        with TemporaryDirectory() as temp_file:
            subprocess.run(["git", "init", temp_file], check=True)

            dataset_tree = create_dataset_tree(initial_dataset_paths, initial_file_paths)
            new_dataset_tree = self.save_load_compare(dataset_tree, temp_file, initial_dataset_paths)

            new_dataset_tree.add_dataset(
                MetadataPath("s/t/u"),
                MetadataRootRecord(uuid_0, "11111", Metadata(), FileTree()))
            new_paths = [p[0] for p in new_dataset_tree.get_paths_recursive()]
            self.assertEqual(len(initial_dataset_paths) + 1, len(new_paths))

            updated_dataset_tree = self.save_load_compare(new_dataset_tree, temp_file, new_paths)
            return


if __name__ == '__main__':
    unittest.main()
