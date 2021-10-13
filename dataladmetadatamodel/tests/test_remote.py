import unittest
from ..common import get_top_level_metadata_objects


class TestRemote(unittest.TestCase):

    def test_basic_remote(self):
        tree_version_list, uuid_set = get_top_level_metadata_objects(
            "git",
            "https://github.com/datalad/test_metadata"
        )
        self.assertEqual(len(tree_version_list.version_set), 1)
        self.assertEqual(len(uuid_set.uuid_set), 1)
