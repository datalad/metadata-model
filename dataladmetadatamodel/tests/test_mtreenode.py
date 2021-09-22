import unittest

from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.text import Text


default_paths = [
    "a/0",
    "a/1",
    "a/b/0",
    "a/b/1",
    "a/b/2"
]


class TestMTreeNode(unittest.TestCase):

    def test_basic(self):
        MTreeNode(Text)

    def test_adding(self):
        mtree_node = MTreeNode(Text)

        for path in default_paths:
            mtree_node.add_child_at(Text(f"content of: {path}"),
                                    MetadataPath(path))

        all_children = list(mtree_node.get_paths_recursive())
        self.assertEqual(len(default_paths), len(all_children))
        for path, child in all_children:
            self.assertIn(str(path), default_paths)
            self.assertIsInstance(child, Text)
            self.assertEqual(child.content, f"content of: {str(path)}")


if __name__ == '__main__':
    unittest.main()
