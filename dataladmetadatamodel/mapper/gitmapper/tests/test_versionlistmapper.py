import time
import unittest
from unittest import mock
from uuid import UUID

from .... import version_string
from ....tests.utils import create_file_tree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.versionlist import (
    VersionList,
    VersionRecord
)


test_realm_name = "ewkd0iasd"

uuid_0 = UUID("00000000000000000000000000000000")


def get_location(n: int) -> str:
    return f"a{n:04}0000000000000000000000000000000{n:04}"


class TestVersionListMapper(unittest.TestCase):

    def test_basic_unmapping(self):

        with mock.patch("dataladmetadatamodel.mapper.gitmapper.versionlistmapper.git_save_json") as save_json, \
             mock.patch("dataladmetadatamodel.mapper.gitmapper.metadatamapper.git_save_str") as save_str, \
             mock.patch("dataladmetadatamodel.mapper.gitmapper.versionlistmapper.git_update_ref") as update_ref:

            save_json.configure_mock(return_value=get_location(0))
            save_str.configure_mock(return_value=get_location(1))

            version_list = VersionList()
            version_list.write_out("/tmp/t1")
            representation = save_json.call_args[0][1]
            self.assertEqual(representation, [])


    def test_complex_unmapping(self):

        with mock.patch("dataladmetadatamodel.mapper.gitmapper.versionlistmapper.git_save_json") as save_json, \
             mock.patch("dataladmetadatamodel.mapper.gitmapper.metadatamapper.git_save_str") as save_str, \
             mock.patch("dataladmetadatamodel.mapper.gitmapper.metadatarootrecordmapper.git_save_json") as save_json_2, \
             mock.patch("dataladmetadatamodel.mapper.gitmapper.mtreenodemapper.git_save_tree_node") as save_tree_node, \
             mock.patch("dataladmetadatamodel.mapper.gitmapper.versionlistmapper.git_update_ref") as update_ref:

            save_json.configure_mock(return_value=get_location(0))
            save_str.configure_mock(return_value=get_location(1))
            save_json_2.configure_mock(return_value=get_location(3))
            save_tree_node.configure_mock(return_value=get_location(4))

            version_list = VersionList(initial_set={
                "v0": VersionRecord(
                    str("1.1"),
                    MetadataPath("subset0"),
                    MetadataRootRecord(
                        uuid_0,
                        "version1",
                        Metadata(),
                        create_file_tree([MetadataPath("a/b"), MetadataPath("d/e")])
                    )
                )
            })

            version_list.write_out("/tmp/t1")
            representation = save_json.call_args[0][1]
            self.assertEqual(
                representation,
                [{
                    'primary_data_version': 'v0',
                    'time_stamp': '1.1',
                    'path': 'subset0',
                    'dataset_tree': {
                        '@': {
                            'type': 'Reference',
                            'version': '2.0'
                        },
                        'mapper_family': 'git',
                        'realm': '/tmp/t1',
                        'class_name': 'MetadataRootRecord',
                        'location': 'a000300000000000000000000000000000000003'
                    }
                }]
            )


if __name__ == '__main__':
    unittest.main()
