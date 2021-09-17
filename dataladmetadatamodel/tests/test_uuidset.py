import unittest
from unittest.mock import patch
from uuid import UUID

from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.uuidset import (
    UUIDSet,
    VersionList,
)
from dataladmetadatamodel.versionlist import VersionRecord


uuid_0 = UUID("00000000000000000000000000000000")
uuid_1 = UUID("00000000000000000000000000000001")
uuid_2 = UUID("00000000000000000000000000000002")


class TestUUIDSet(unittest.TestCase):

    def test_basic(self):
        UUIDSet()

    def test_deepcopy(self):
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

        with patch("dataladmetadatamodel.mapper.gitmapper.datasettreemapper.git_save_tree") as save_tree:
            save_tree.configure_mock(return_value="00000000011111")
            copied_uuid_set = uuid_set.deepcopy("git", "/tmp/new")
            print(copied_uuid_set)


if __name__ == '__main__':
    unittest.main()
