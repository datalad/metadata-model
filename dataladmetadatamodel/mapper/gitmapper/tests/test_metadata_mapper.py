import json
import unittest
from unittest import mock

from dataladmetadatamodel.metadata import (
    ExtractorConfiguration,
    Metadata
)

from .... import version_string


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

        with mock.patch("dataladmetadatamodel.mapper.gitmapper.metadatamapper.git_save_str") as save:

            save.configure_mock(return_value="0000011111")

            reference = metadata.write_out("/tmp/t1", "git")
            save.assert_called_once()
            representation = save.call_args[0][1]
            self.assertEqual(
                json.loads(representation),
                {
                    "@": {
                        "type": "Metadata",
                        "version": "2.0"
                    },
                    "instance_sets": {
                        "test-extractor": {
                            "@": {
                                "type": "MetadataInstanceSet",
                                "version": "2.0"
                            },
                            "parameter_set": [
                                {
                                    "@": {
                                        "type": "ExtractorConfiguration",
                                        "version": "2.0"
                                    },
                                    "version": "v3.4",
                                    "parameter": {"p1": "1"}
                                }
                            ],
                            "instance_set": {
                                "0": {
                                    "@": {
                                        "type": "MetadataInstance",
                                        "version": "2.0"
                                    },
                                    "time_stamp": 1.2,
                                    "author": "test-tool",
                                    "author_email": "test-tool@test.com",
                                    "configuration": {
                                        "@": {
                                            "type": "ExtractorConfiguration",
                                            "version": "2.0"
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
            )


if __name__ == '__main__':
    unittest.main()
