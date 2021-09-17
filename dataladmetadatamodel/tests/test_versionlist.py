import subprocess
import tempfile
import unittest
from uuid import UUID

from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.versionlist import (
    VersionList,
    VersionRecord
)

from .utils import MMDummy


uuid_0 = UUID("00000000000000000000000000000000")
uuid_1 = UUID("00000000000000000000000000000001")
uuid_2 = UUID("00000000000000000000000000000002")


class TestVersionList(unittest.TestCase):

    def test_basic(self):
        version_list = VersionList()

    def test_deepcopy(self):
        version_list = VersionList(initial_set={
            "v1": VersionRecord(
                "0.1",
                MetadataPath("a"),
                MMDummy()
            ),
            "v2": VersionRecord(
                "0.2",
                MetadataPath("b"),
                MMDummy()
            )
        })

        copied_version_list = version_list.deepcopy(
            path_prefix=MetadataPath("x/y/z")
        )
        print(copied_version_list)


class XTestDeepCopy(unittest.TestCase):

    def xtest_copy_from_memory(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])

    def xtest_copy_from_backend(self):
        with \
                tempfile.TemporaryDirectory() as original_dir, \
                tempfile.TemporaryDirectory() as copy_dir:

            subprocess.run(["git", "init", original_dir])
            subprocess.run(["git", "init", copy_dir])


if __name__ == '__main__':
    unittest.main()
