import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List

from ..objectreference import flush_object_references
from ..filetreemapper import FileTreeGitMapper
from ....filetree import FileTree
from ....metadata import Metadata
from ....metadatapath import MetadataPath
from ....tests.utils import create_file_tree_with_metadata


initial_paths = [
    MetadataPath("a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x")
]


class TestFileTreeMapper(unittest.TestCase):

    def save_load_compare(self, file_tree: FileTree, realm: str, expected_paths: List[MetadataPath]) -> FileTree:
        reference = file_tree.save()
        file_tree = None
        flush_object_references(Path(realm))

        new_file_tree = FileTreeGitMapper(realm).map(reference)
        loaded_paths = [p[0] for p in new_file_tree.get_paths_recursive()]

        self.assertEqual(len(loaded_paths), len(expected_paths))
        self.assertTrue(all(map(lambda np: np in expected_paths, loaded_paths)))
        return new_file_tree

    # Ensure that updates do not destroy existing git-trees
    def test_load_update_write(self):
        with TemporaryDirectory() as temp_file:
            subprocess.run(["git", "init", temp_file], check=True)

            file_tree = create_file_tree_with_metadata(
                "git",
                temp_file,
                initial_paths,
                [
                    Metadata("git", temp_file)
                    for _ in initial_paths
                ])

            new_file_tree = self.save_load_compare(file_tree, temp_file, initial_paths)

            new_file_tree.add_metadata(MetadataPath("s/t/u"), Metadata("git", temp_file))
            new_paths = [p[0] for p in new_file_tree.get_paths_recursive()]
            self.assertEqual(len(initial_paths) + 1, len(new_paths))

            updated_file_tree = self.save_load_compare(new_file_tree, temp_file, new_paths)


if __name__ == '__main__':
    unittest.main()