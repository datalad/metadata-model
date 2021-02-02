import unittest

from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata


class TestGenerator(unittest.TestCase):
    def test_generator(self):

        paths = ["a/b/c", "a/b/a", "b", "c/d/e"]

        file_tree = FileTree("git", "/tmp")
        metadata_node = Metadata("git", "/tmp")
        for path in paths:
            file_tree.add_metadata(path, metadata_node)

        returned_entries = tuple(file_tree.get_paths_recursive())

        returned_paths = [entry[0] for entry in returned_entries]
        self.assertEqual(sorted(paths), sorted(returned_paths))

        returned_metadata = set([entry[1].object for entry in returned_entries])
        self.assertEqual(returned_metadata, {metadata_node})


if __name__ == '__main__':
    unittest.main()
