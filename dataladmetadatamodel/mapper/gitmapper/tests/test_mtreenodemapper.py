import unittest
from unittest import mock

from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.text import Text


tree_location = "a000000000000000000000000000000000000000"
file_location = "a001000000000000000000000000000000000001"


class TestMTreeNodeMapper(unittest.TestCase):

    def test_basic_unmapping(self):

        realm = "/tmp/t1"
        file_names = ["a", "b", "c"]
        sub_dir_names = ["sub0", "sub1", "sub2"]

        root_node = MTreeNode(Text)
        for sub_dir_name in sub_dir_names:
            sub_tree_node = MTreeNode(Text)
            for file_name in file_names:
                sub_tree_node.add_child(
                    file_name,
                    Text(f"content of: /{sub_dir_name}/{file_name}"))
            root_node.add_child(sub_dir_name, sub_tree_node)

        with \
                mock.patch(
                "dataladmetadatamodel.mapper.gitmapper"
                ".mtreenodemapper.git_save_tree_node") as save_tree_node, \
                mock.patch(
                    "dataladmetadatamodel.mapper.gitmapper" 
                    ".textmapper.git_save_str") as save_str:

            save_tree_node.configure_mock(return_value=tree_location)
            save_str.configure_mock(return_value=file_location)

            reference = root_node.write_out(realm, "git")

            # Expect one (root) plus three (sub-dir trees) calls
            self.assertEqual(save_tree_node.call_count, 4)

            expected_sub_tree_calls = [
                mock.call(
                    realm,
                    [
                        ("100644", "blob", file_name, file_location)
                        for file_name in file_names
                    ]
                )
                for _ in range(3)
            ]
            save_tree_node.assert_has_calls(expected_sub_tree_calls, any_order=True)

            expected_root_calls = [
                mock.call(
                    realm,
                    [
                        ("040000", "tree", sub_dir_name, tree_location)
                        for sub_dir_name in sub_dir_names
                    ]
                )
            ]
            save_tree_node.assert_has_calls(expected_root_calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
