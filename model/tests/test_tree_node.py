import unittest

from model.treenode import TreeNode


class TestHierarchy(unittest.TestCase):
    def test_hierarchical_adding(self):
        paths = ["a/b/c", "a/b/a", "b", "c/d/e"]
        tree = TreeNode()

        for path in paths:
            tree.add_node_hierarchy(path, TreeNode(value=path))

        leaf_path_infos = tree.get_paths_recursive(False)
        leaf_path_names = [info[0] for info in leaf_path_infos]
        self.assertEqual(sorted(paths), sorted(leaf_path_names))
        self.assertIsNotNone(tree.get_node_at_path("a"))
        self.assertIsNotNone(tree.get_node_at_path("a/b"))
        self.assertIsNotNone(tree.get_node_at_path("a/b/c"))
        self.assertIsNone(tree.get_node_at_path("a/b/c/d"))
        self.assertIsNone(tree.get_node_at_path("a/b/x"))

    def test_existing_path(self):
        tree = TreeNode()
        tree.add_node_hierarchy("a/b/c", TreeNode(value="test-value"))
        self.assertRaises(ValueError, tree.add_node_hierarchy, "a/b/c", TreeNode(value="test-value"))
        self.assertRaises(ValueError, tree.add_node_hierarchy, "a/b", TreeNode(value="test-value"))
        self.assertRaises(ValueError, tree.add_node_hierarchy, "a", TreeNode(value="test-value"))


if __name__ == '__main__':
    unittest.main()
