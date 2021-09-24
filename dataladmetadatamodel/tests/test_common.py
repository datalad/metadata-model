import unittest

from dataladmetadatamodel.common import (
    get_top_level_metadata_objects,
    get_top_nodes_and_metadata_root_record
)
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.tests.utils import get_uuid


uuid_0 = get_uuid(0)


class TestTopLevelObjects(unittest.TestCase):
    @unittest.skip
    def test_top_level_metadata_objects(self):
        a, b = get_top_level_metadata_objects(
            "git",
            "/home/henry/datalad/inm7-studies/superset"
        )
        print(a, b)

    @unittest.skip
    def test_top_nodes_and_metadata_root_record(self):
        a, b, c = get_top_nodes_and_metadata_root_record(
            "git",
            "/home/henry/datalad/inm7-studies/superset",
            uuid_0,
            "v1",
            MetadataPath("a/b/c"),
            True
        )
        print(a, b, c)


if __name__ == '__main__':
    unittest.main()
