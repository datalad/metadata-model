import unittest
from unittest import mock
from uuid import UUID

from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.tests.utils import create_file_tree_with_metadata

from .... import version_string


uuid_0 = UUID("00000000000000000000000000000000")
dataset_version = "000000011111222223333"
location_0 = "a000000000000000000000000000000000000000"
location_1 = "a000000000000000000000000000000000000001"
location_2 = "a000000000000000000000000000000000000002"
location_3 = "a000000000000000000000000000000000000003"


default_paths = [
    MetadataPath("a/b/c"),
    MetadataPath("a/b/a"),
    MetadataPath("b"),
    MetadataPath("c/d/e"),
    MetadataPath("a/x")
]


class TestMetadataMapper(unittest.TestCase):

    def test_basic_unmapping(self):

        file_tree = create_file_tree_with_metadata(default_paths, [
            Metadata()
            for _ in default_paths])

        mrr = MetadataRootRecord(
            uuid_0,
            dataset_version,
            Metadata(),
            file_tree)

        with mock.patch("dataladmetadatamodel.mapper.gitmapper.metadatarootrecordmapper.git_save_json") as save, \
             mock.patch("dataladmetadatamodel.mapper.gitmapper.metadatamapper.git_save_str") as str_save, \
             mock.patch("dataladmetadatamodel.mapper.gitmapper.mtreenodemapper.git_save_tree_node") as save_tree_node:

            save.configure_mock(return_value=location_0)
            str_save.configure_mock(return_value=location_1)
            save_tree_node.configure_mock(return_value=location_3)

            reference = mrr.write_out("/tmp/t1", "git")
            self.assertEqual(reference.location, location_0)

            save.assert_called_once()
            representation = save.call_args[0][1]
            self.assertEqual(
                representation,
                {
                    'dataset_identifier': str(uuid_0),
                    'dataset_version': dataset_version,
                    'dataset_level_metadata': {
                        '@': {
                            'type': 'Reference',
                            'version': version_string
                        },
                        'class_name': 'Metadata',
                        'location': location_1
                    },
                    'file_tree': {
                        '@': {
                            'type': 'Reference',
                            'version': version_string
                        },
                        'class_name': 'MTreeNode',
                        'location': location_3}
                }
            )


if __name__ == '__main__':
    unittest.main()
