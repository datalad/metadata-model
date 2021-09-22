import json
import unittest
from unittest import mock

from .... import version_string
from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.text import Text


location_0 = "a000000000000000000000000000000000000000"
location_1 = "a001000000000000000000000000000000000001"


expected_reference_object = {
    "@": {
        "type": "Reference",
        "version": version_string
    },
    "mapper_family": "git",
    "realm": "/tmp/t1",
    "class_name": "Metadata",
    "location": location_0
}


expected_metadata_object = {
    "@": {
        "type": "Metadata",
        "version": version_string
    },
    "instance_sets": {
        "test-extractor": {
            "@": {
                "type": "MetadataInstanceSet",
                "version": version_string
            },
            "parameter_set": [
                {
                    "@": {
                        "type": "ExtractorConfiguration",
                        "version": version_string
                    },
                    "version": "v3.4",
                    "parameter": {"p1": "1"}
                }
            ],
            "instance_set": {
                "0": {
                    "@": {
                        "type": "MetadataInstance",
                        "version": version_string
                    },
                    "time_stamp": 1.2,
                    "author": "test-tool",
                    "author_email": "test-tool@test.com",
                    "configuration": {
                        "@": {
                            "type": "ExtractorConfiguration",
                            "version": version_string
                        },
                        "version": "v3.4",
                        "parameter": {"p1": "1"}
                    },
                    "metadata_content": {
                        "key1": "this is metadata"
                    }
                }
            }
        }
    }
}


class TestMTreeNodeMapper(unittest.TestCase):

    def test_basic_unmapping(self):
        mtree_node = MTreeNode(None)

        for child_name in ["a", "b", "c"]:
            mtree_node.add_child(
                child_name,
                Text(f"content of: {child_name}"))

        for child_name in ["sub0", "sub1", "sub2"]:
            mtree_node.add_child(
                child_name,
                MTreeNode(MTreeNode))

        with \
                mock.patch(
                "dataladmetadatamodel.mapper.gitmapper"
                ".mtreenodemapper.git_save_tree_node") as save_tree_node, \
                mock.patch(
                    "dataladmetadatamodel.mapper.gitmapper" 
                    ".textmapper.git_save_str") as save_str:

            save_tree_node.configure_mock(return_value=location_0)
            save_str.configure_mock(return_value=location_1)

            reference = mtree_node.write_out("/tmp/t1", "git")
            self.assertEqual(len(save_tree_node.call_args_list), 2)
            self.assertEqual(
                json.loads(save_tree_node.call_args_list[0][0][1]),
                expected_metadata_object)
            self.assertEqual(
                json.loads(save_tree_node.call_args_list[1][0][1]),
                expected_reference_object)


if __name__ == '__main__':
    unittest.main()
