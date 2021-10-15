import subprocess
import tempfile
import unittest
from typing import List
from unittest import mock

from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.text import Text
from dataladmetadatamodel.mapper.reference import Reference


tree_location = "a000000000000000000000000000000000000000"
file_location = "a001000000000000000000000000000000000001"


def create_tree(file_names: List[str],
                sub_dir_names: List[str]
                ) -> MTreeNode:

    root_node = MTreeNode(Text)
    for sub_dir_name in sub_dir_names:
        sub_tree_node = MTreeNode(Text)
        for file_name in file_names:
            sub_tree_node.add_child(
                file_name,
                Text(f"content of: /{sub_dir_name}/{file_name}"))
        root_node.add_child(sub_dir_name, sub_tree_node)
    return root_node


class TestMTreeNodeMapper(unittest.TestCase):

    def test_basic_unmapping(self):

        realm = "/tmp/t1"
        file_names = ["a", "b", "c"]
        sub_dir_names = ["sub0", "sub1", "sub2"]

        root_node = create_tree(file_names, sub_dir_names)

        with \
                mock.patch(
                    "dataladmetadatamodel.mapper.gitmapper"
                    ".mtreenodemapper.git_save_tree_node") as save_tree_node, \
                mock.patch(
                    "dataladmetadatamodel.mapper.gitmapper" 
                    ".textmapper.git_save_str") as save_str:

            save_tree_node.configure_mock(return_value=tree_location)
            save_str.configure_mock(return_value=file_location)

            root_node.write_out(realm, "git")

            # Expect one (root) plus three (sub-dir trees) calls
            self.assertEqual(save_tree_node.call_count, 4)

            expected_sub_tree_calls = [
                mock.call(
                    realm,
                    [
                        ("100644", "blob", file_location, file_name)
                        for file_name in file_names
                    ]
                )
                for _ in range(len(sub_dir_names))
            ]
            save_tree_node.assert_has_calls(expected_sub_tree_calls, any_order=True)

            expected_root_calls = [
                mock.call(
                    realm,
                    [
                        ("040000", "tree", tree_location, sub_dir_name)
                        for sub_dir_name in sub_dir_names
                    ]
                )
            ]
            save_tree_node.assert_has_calls(expected_root_calls, any_order=True)

    def test_none_mapping_out(self):
        tree = MTreeNode(Text)
        reference = tree.write_out("/tmp/t1")
        self.assertTrue(reference.is_none_reference())

    def test_none_mapping_in(self):
        reference = Reference.get_none_reference("MTreeNode")
        tree = MTreeNode(Text, "/tmp/t1", reference)
        tree.read_in()
        self.assertEqual(len(tree.child_nodes), 0)

    def test_mapping_end_to_end(self):
        file_names = ["a", "b", "c"]
        sub_dir_names = ["sub0", "sub1", "sub2"]

        with tempfile.TemporaryDirectory() as realm:

            subprocess.run(["git", "init", realm])

            root_node = create_tree(file_names, sub_dir_names)
            reference = root_node.write_out(realm)

            new_root_node = MTreeNode(
                leaf_class=Text,
                realm=realm,
                reference=reference)
            new_root_node.read_in()

            tree_elements = list(new_root_node.get_paths_recursive())
            self.assertEqual(len(tree_elements),
                             len(file_names) * len(sub_dir_names))
            self.assertEqual(
                [str(tree_element[0]) for tree_element in tree_elements],
                [
                    sub_dir_name + "/" + file_name
                    for sub_dir_name in sub_dir_names
                    for file_name in file_names
                ]
            )

            self.assertEqual(
                [
                    tree_element[1].read_in().content
                    for tree_element in tree_elements
                ],
                [
                    f"content of: /{sub_dir_name}/{file_name}"
                    for sub_dir_name in sub_dir_names
                    for file_name in file_names
                ]
            )


if __name__ == '__main__':
    unittest.main()
