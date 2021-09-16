import unittest
from uuid import UUID

from dataladmetadatamodel.common import (
    get_top_level_metadata_objects,
    get_top_nodes_and_metadata_root_record
)
from dataladmetadatamodel.metadatapath import MetadataPath


uuid_0 = UUID("00000000000000000000000000000000")


class TestTopLevelObjects(unittest.TestCase):

    def test_top_level_metadata_objects(self):
        a, b = get_top_level_metadata_objects(
            "git",
            "/home/cristian/datalad/inm7-studies/superset"
        )
        print(a, b)


    def test_top_nodes_and_metadata_root_record(self):
        a, b, c = get_top_nodes_and_metadata_root_record(
            "git",
            "/home/cristian/datalad/inm7-studies/superset",
            uuid_0,
            "v1",
            MetadataPath("a/b/c"),
            True
        )
        print(a, b, c)


if __name__ == '__main__':
    unittest.main()
