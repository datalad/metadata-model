import subprocess
import tempfile
import unittest

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.uuidset import (
    UUIDSet,
    VersionList,
)
from dataladmetadatamodel.versionlist import VersionRecord

from .utils import (
    assert_uuid_sets_equal,
    create_dataset_tree,
    get_uuid
)


uuid_0 = get_uuid(0)
uuid_1 = get_uuid(1)
uuid_2 = get_uuid(2)


class TestUUIDSet(unittest.TestCase):

    def test_basic(self):
        UUIDSet()

    def test_copy_from_memory(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            uuid_set = UUIDSet(initial_set={
                uuid_0: VersionList(initial_set={
                    "v0": {
                        MetadataPath("path0"): VersionRecord(
                            "1.2",
                            MetadataPath("path0"),
                            create_dataset_tree()
                        )
                    }
                }),
                uuid_1: VersionList(initial_set={
                    "v0.0": {
                        MetadataPath("path0.0"): VersionRecord(
                            "1.3",
                            MetadataPath("path0.0"),
                            create_dataset_tree()
                        )
                    }
                })
            })

            copied_uuid_set = uuid_set.deepcopy(new_destination=copy_dir)
            copied_uuid_set.read_in()
            assert_uuid_sets_equal(self, uuid_set, copied_uuid_set)

    def test_copy_from_backend(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            uuid_set = UUIDSet(initial_set={
                uuid_0: VersionList(initial_set={
                    "v0": {
                        MetadataPath("path0"): VersionRecord(
                            "1.2",
                            MetadataPath("path0"),
                            create_dataset_tree()
                        )
                    }
                }),
                uuid_1: VersionList(initial_set={
                    "v0.0": {
                        MetadataPath("path0.0"): VersionRecord(
                            "1.3",
                            MetadataPath("path0.0"),
                            create_dataset_tree()
                        )
                    }
                })
            })

            uuid_set.write_out(original_dir)
            uuid_set_copy = uuid_set.deepcopy(new_destination=copy_dir)

            # assert that the purged uuid-sets are equal
            uuid_set.purge()
            assert_uuid_sets_equal(self, uuid_set, uuid_set_copy)

            # load both and compare the uuid set level
            uuid_set.read_in()
            uuid_set_copy.read_in()
            assert_uuid_sets_equal(self, uuid_set, uuid_set_copy)


if __name__ == '__main__':
    unittest.main()
