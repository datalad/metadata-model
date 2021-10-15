import subprocess
import tempfile
import time
import unittest

from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.text import Text


default_paths = [
    "x",
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

    def test_get_paths_recursive(self):
        mtree_node = MTreeNode(Text)

        for path in default_paths:
            mtree_node.add_child_at(Text(f"content of: {path}"),
                                    MetadataPath(path))
        results = list(mtree_node.get_paths_recursive())
        returned_paths = set(map(lambda e: str(e[0]), results))
        self.assertSetEqual(set(default_paths), returned_paths)

    def test_get_paths_recursive_intermediate(self):
        mtree_node = MTreeNode(Text)

        for path in default_paths:
            mtree_node.add_child_at(Text(f"content of: {path}"),
                                    MetadataPath(path))
        results = list(mtree_node.get_paths_recursive(True))

        intermediate = set([
            "/".join(path.split("/")[:i])
            for path in default_paths
            for i in range(len(path))
        ] + default_paths)

        returned_paths = set(map(lambda e: str(e[0]), results))
        self.assertSetEqual(intermediate, returned_paths)


class TestMTreeNodeMapping(unittest.TestCase):

    def test_adding_to_massive_tree(self):
        with tempfile.TemporaryDirectory() as metadata_store:

            subprocess.run(["git", "init", metadata_store])

            mtree = MTreeNode(leaf_class=Text)

            start_time = time.time()
            for first_part in range(10):
                for second_part in range(10):
                    for third_part in range(10):
                        metadata_path = MetadataPath(f"{first_part:03}/"
                                                     f"{second_part:03}/"
                                                     f"{third_part:03}")
                        mtree.add_child_at(
                            Text(content=f"content of: {str(metadata_path)}"),
                            metadata_path)

            initialisation_duration = time.time() - start_time
            print(f"Initialised: {initialisation_duration:4f}")

            start_time = time.time()
            reference = mtree.write_out(metadata_store)
            write_out_duration = time.time() - start_time
            print(f"Written out: {write_out_duration:4f}")

            mtree = MTreeNode(leaf_class=Text,
                              realm=metadata_store,
                              reference=reference)
            start_time = time.time()
            mtree.read_in()
            read_in_duration = time.time() - start_time
            print(f"Read in: {read_in_duration:4f}")

            metadata_path = MetadataPath("5/5/xxx")
            start_time = time.time()
            mtree.add_child_at(
                Text(content=f"content of: {str(metadata_path)}"),
                metadata_path)
            add_duration = time.time() - start_time
            print(f"Added single entry: {add_duration:4f}")

            start_time = time.time()
            mtree.write_out()
            write_out_2nd_duration = time.time() - start_time
            print(f"Written out single entry: {write_out_2nd_duration:4f}")


if __name__ == '__main__':
    unittest.main()
