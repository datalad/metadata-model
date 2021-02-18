import subprocess
import tempfile
import unittest

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata


class TestFileTree(unittest.TestCase):
    def test_add_metadata(self):

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

    def test_root_node(self):
        file_tree = FileTree("git", "/tmp")
        metadata_node = Metadata("git", "/tmp")
        file_tree.add_metadata("", metadata_node)

        expected_connector = Connector.from_object(metadata_node)
        self.assertEqual(file_tree.value, expected_connector)
        returned_entries = tuple(file_tree.get_paths_recursive())

        self.assertEqual(len(returned_entries), 1)
        self.assertEqual(returned_entries[0][0], "")
        self.assertEqual(returned_entries[0][1], expected_connector)


class TestDeepCopy(unittest.TestCase):

    def _compare_file_trees(self, a: FileTree, b: FileTree):
        a_entries = list(a.get_paths_recursive())
        b_entries = list(b.get_paths_recursive())

        # Compare paths
        self.assertListEqual(
            list(map(lambda x: x[0], a_entries)),
            list(map(lambda x: x[0], b_entries)))

        # Compare metadata elements
        for a_connector, b_connector in zip(
                map(lambda x: x[1], a_entries),
                map(lambda x: x[1], b_entries)):

            a_metadata = a_connector.load_object(a_connector.reference.mapper_family, a_connector.reference.realm)
            b_metadata = b_connector.load_object(b_connector.reference.mapper_family, b_connector.reference.realm)

            self.assertEqual(a_metadata.instance_sets, b_metadata.instance_sets)

            a_connector.purge()
            b_connector.purge()


    def test_copy_from_memory(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            file_tree = FileTree("git", original_dir)
            file_tree.add_metadata("", Metadata("git", original_dir))
            file_tree.add_metadata("/a/b/c/d", Metadata("git", original_dir))
            file_tree.add_metadata("/a/b/d", Metadata("git", original_dir))
            file_tree.add_metadata("/a/x", Metadata("git", original_dir))

            file_tree_copy = file_tree.deepcopy("git", copy_dir)

            self._compare_file_trees(file_tree, file_tree_copy)

    def test_copy_from_backend(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            paths = ["", "a/b/c/d", "a/b/d", "a/x"]
            file_tree = FileTree("git", original_dir)
            for path in paths:
                file_tree.add_metadata(path, Metadata("git", original_dir))
                file_tree.unget_metadata(path)
            file_tree.save()

            file_tree_copy = file_tree.deepcopy("git", copy_dir)

            self._compare_file_trees(file_tree, file_tree_copy)




if __name__ == '__main__':
    unittest.main()
