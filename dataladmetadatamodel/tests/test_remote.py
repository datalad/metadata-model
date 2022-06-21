import unittest
from typing import cast

from dataladmetadatamodel.common import get_top_level_metadata_objects
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath


class TestRemote(unittest.TestCase):

    def test_basic_remote(self):
        tree_version_list, uuid_set = get_top_level_metadata_objects(
            "git",
            "https://github.com/datalad/test_metadata"
        )
        self.assertEqual(len(tree_version_list.version_set), 2)
        self.assertEqual(len(uuid_set.uuid_set), 2)

        for version, element_info in tree_version_list.versioned_elements:
            # Ignore versions that are not known
            if version == "73ad0039ade25bd0f6b0dbf9dd13006e3721cc38":
                break
            time_stamp, dataset_path, dataset_tree = element_info
            dataset_tree = cast(DatasetTree, dataset_tree)
            dataset_tree.read_in()
            dataset_paths = dataset_tree.dataset_paths
            self.assertEqual(27, len(dataset_paths))

            mrr = dataset_tree.get_metadata_root_record(MetadataPath("study-104"))
            file_tree = mrr.file_tree
            file_paths = list(file_tree.get_paths_recursive())
            self.assertEqual(7, len(file_paths))

            file_tree.add_metadata(MetadataPath("a/b/c"), Metadata())
            self.assertRaises(RuntimeError, file_tree.write_out)
