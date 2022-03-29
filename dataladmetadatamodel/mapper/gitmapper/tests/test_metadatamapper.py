import json
import unittest
from pathlib import Path
from typing import cast
from unittest import mock

from .... import version_string
from ....tests.utils import get_location
from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.mapper.gitmapper.metadatamapper import MetadataGitMapper
from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references
from dataladmetadatamodel.metadata import (
    ExtractorConfiguration,
    Metadata
)


expected_reference_object = {
    "@": {
        "type": "Reference",
        "version": version_string
    },
    "class_name": "Metadata",
    "location": get_location(1)
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


class TestMetadataMapper(unittest.TestCase):

    def test_basic_unmapping(self):
        metadata = Metadata()
        metadata.add_extractor_run(
            1.2,
            "test-extractor",
            "test-tool",
            "test-tool@test.com",
            ExtractorConfiguration("v3.4", {"p1": "1"}),
            {"key1": "this is metadata"})

        with \
                mock.patch("dataladmetadatamodel.mapper.gitmapper"
                           ".metadatamapper.git_save_str") as save_str, \
                mock.patch("dataladmetadatamodel.mapper.gitmapper"
                           ".treeupdater.git_save_tree_node") as save_tree_node, \
                mock.patch("dataladmetadatamodel.mapper.gitmapper"
                           ".gitbackend.subprocess.git_update_ref") as update_ref:

            save_str.return_value = get_location(1)
            save_tree_node.return_value = get_location(2)
            update_ref.return_value = get_location(3)

            realm = "/tmp/t1"
            reference = metadata.write_out(realm, "git")
            flush_object_references(Path("/tmp/t1"))

            self.assertEqual(len(save_str.call_args_list), 2)
            self.assertEqual(
                json.loads(save_str.call_args_list[0][0][1]),
                expected_metadata_object)
            self.assertEqual(
                json.loads(save_str.call_args_list[1][0][1]),
                expected_reference_object)

    def test_double_cache_detection(self):
        metadata_mapper: MetadataGitMapper = cast(
            MetadataGitMapper,
            get_mapper("Metadata", "git")
        )
        metadata_mapper.cache_realm("a")
        self.assertRaises(RuntimeError, metadata_mapper.cache_realm, "a")
        self.assertRaises(RuntimeError, metadata_mapper.flush_realm, "err")


if __name__ == '__main__':
    unittest.main()
