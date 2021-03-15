import unittest

from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.treenode import TreeNode


class TestHierarchy(unittest.TestCase):
    def test_hierarchical_adding(self):
        paths = [
            MetadataPath("a/b/c"),
            MetadataPath("a/b/a"),
            MetadataPath("b"),
            MetadataPath("c/d/e")]

        tree = TreeNode()

        for path in paths:
            tree.add_node_hierarchy(path, TreeNode(value=path))

        leaf_path_names = [info[0] for info in tree.get_paths_recursive(False)]
        self.assertEqual(sorted(paths), sorted(leaf_path_names))

        for path in [MetadataPath("a"),
                     MetadataPath("a/b"),
                     MetadataPath("a/b/c")]:
            self.assertIsNotNone(tree.get_node_at_path(path))

        for path in [MetadataPath("a/b/c/d"),
                     MetadataPath("a/b/x")]:
            self.assertIsNone(tree.get_node_at_path(path))

    def test_existing_path(self):
        tree = TreeNode()
        tree.add_node_hierarchy(
            MetadataPath("a/b/c"),
            TreeNode(value="test-value"))

        for path in [MetadataPath("a/b/c"),
                     MetadataPath("a/b"),
                     MetadataPath("a")]:

            self.assertRaises(
                ValueError,
                tree.add_node_hierarchy,
                path,
                TreeNode(value="test-value"))

    def test_all_nodes_in_path(self):
        tree = TreeNode()
        tree.add_node_hierarchy(
            MetadataPath("a/b/c"),
            TreeNode(value="test-value1"))
        tree.add_node_hierarchy(
            MetadataPath("a/b/d"),
            TreeNode(value="test-value2"))

        self.assertEqual(
            tree.get_all_nodes_in_path(),
            tree.get_all_nodes_in_path(MetadataPath("")))

        all_nodes_in_path = tree.get_all_nodes_in_path(MetadataPath(""))
        self.assertEqual(len(all_nodes_in_path), 1)
        self.assertEqual(all_nodes_in_path[0][0], "")
        all_nodes_in_path = tree.get_all_nodes_in_path(MetadataPath("a/b/c"))
        self.assertEqual(len(all_nodes_in_path), 4)


if __name__ == '__main__':
    unittest.main()
