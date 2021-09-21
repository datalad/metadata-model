import json
import unittest
from unittest import mock

from .... import version_string
from dataladmetadatamodel.metadata import (
    ExtractorConfiguration,
    Metadata
)


location_0 = "a000000000000000000000000000000000000000"


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


class TestMetadataMapper(unittest.TestCase):

    def test_basic_unmapping(self):
        metadata = Metadata(None)
        metadata.add_extractor_run(
            1.2,
            "test-extractor",
            "test-tool",
            "test-tool@test.com",
            ExtractorConfiguration("v3.4", {"p1": "1"}),
            {"key1": "this is metadata"})

        with mock.patch(
                "dataladmetadatamodel.mapper.gitmapper"
                ".metadatamapper.git_save_str") as save:

            save.configure_mock(return_value=location_0)

            reference = metadata.write_out("/tmp/t1", "git")
            self.assertEqual(len(save.call_args_list), 2)
            self.assertEqual(
                json.loads(save.call_args_list[0][0][1]),
                expected_metadata_object)
            self.assertEqual(
                json.loads(save.call_args_list[1][0][1]),
                expected_reference_object)


if __name__ == '__main__':
    unittest.main()
