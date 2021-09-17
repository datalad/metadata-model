import subprocess
import tempfile
import unittest
from uuid import UUID

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.uuidset import (
    UUIDSet,
    VersionList,
)
from dataladmetadatamodel.versionlist import VersionRecord

from .utils import assert_version_lists_equal


uuid_0 = UUID("00000000000000000000000000000000")
uuid_1 = UUID("00000000000000000000000000000001")
uuid_2 = UUID("00000000000000000000000000000002")


def assert_uuid_sets_equal(test_case: unittest.TestCase,
                           a_uuid_set: UUIDSet,
                           b_uuid_set: UUIDSet):

    for dataset_id in a_uuid_set.uuids():
        a_version_list = a_uuid_set.get_version_list(dataset_id)
        b_version_list = b_uuid_set.get_version_list(dataset_id)
        assert_version_lists_equal(test_case,
                                   a_version_list,
                                   b_version_list,
                                   True)


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
                    "v0": VersionRecord(
                        "1.2",
                        MetadataPath("path0"),
                        DatasetTree()
                    )
                }),
                uuid_1: VersionList(initial_set={
                    "v0.0": VersionRecord(
                        "1.3",
                        MetadataPath("path0.0"),
                        DatasetTree()
                    )
                })
            })

            copied_uuid_set = uuid_set.deepcopy(new_destination=copy_dir)
            assert_uuid_sets_equal(self, uuid_set, copied_uuid_set)

    def test_copy_from_backend(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

            uuid_set = UUIDSet(initial_set={
                uuid_0: VersionList(initial_set={
                    "v0": VersionRecord(
                        "1.2",
                        MetadataPath("path0"),
                        DatasetTree()
                    )
                }),
                uuid_1: VersionList(initial_set={
                    "v0.0": VersionRecord(
                        "1.3",
                        MetadataPath("path0.0"),
                        DatasetTree()
                    )
                })
            })

            uuid_set.write_out(original_dir)
            uuid_set.purge()
            uuid_set_copy = uuid_set.deepcopy(new_destination=copy_dir)

            assert_uuid_sets_equal(self, uuid_set, uuid_set_copy)


if __name__ == '__main__':
    unittest.main()
