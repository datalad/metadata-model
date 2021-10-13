import subprocess
import tempfile
import unittest

from dataladmetadatamodel.common import (
    get_top_level_metadata_objects,
    get_top_nodes_and_metadata_root_record,
)
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.tests.utils import get_uuid
from dataladmetadatamodel.uuidset import UUIDSet
from dataladmetadatamodel.versionlist import TreeVersionList

uuid_0 = get_uuid(0)


class TestTopLevelObjects(unittest.TestCase):

    # This is not exactly a unit test since it does not
    # isolate the units from the other components, but
    # more a module test.
    def test_top_level_functions(self):

        with tempfile.TemporaryDirectory() as realm:
            subprocess.run(["git", "init", realm])

            tvl, uuid_set = get_top_level_metadata_objects("git", realm)
            self.assertIsNone(tvl)
            self.assertIsNone(uuid_set)

            tvl, uuid_set, mrr = get_top_nodes_and_metadata_root_record(
                "git",
                realm,
                uuid_0,
                "v1",
                MetadataPath("a/b/c"),
                False
            )
            self.assertIsNone(tvl)
            self.assertIsNone(uuid_set)
            self.assertIsNone(mrr)

            tvl, uuid_set, mrr = get_top_nodes_and_metadata_root_record(
                "git",
                realm,
                uuid_0,
                "v1",
                MetadataPath("a/b/c"),
                True
            )
            self.assertIsInstance(tvl, TreeVersionList)
            self.assertIsInstance(uuid_set, UUIDSet)
            self.assertIsInstance(mrr, MetadataRootRecord)

            tvl.write_out(realm)
            uuid_set.write_out(realm)

            tvl, uuid_set = get_top_level_metadata_objects("git", realm)
            self.assertIsInstance(tvl, TreeVersionList)
            self.assertIsInstance(uuid_set, UUIDSet)


if __name__ == '__main__':
    unittest.main()
