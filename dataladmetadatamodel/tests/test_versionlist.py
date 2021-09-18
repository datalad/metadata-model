import subprocess
import tempfile
import unittest

from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.versionlist import (
    VersionList,
    VersionRecord
)

from .utils import (
    MMDummy,
    get_uuid,
    get_version
)


class TestVersionList(unittest.TestCase):

    def test_basic(self):
        VersionList()

    def test_deepcopy(self):
        element_0 = MMDummy()
        element_1 = MMDummy()
        version_list = VersionList(initial_set={
            "v1": VersionRecord(
                "0.1",
                MetadataPath("a"),
                element_0
            ),
            "v2": VersionRecord(
                "0.2",
                MetadataPath("b"),
                element_1
            )
        })

        element_1.read_in()

        copied_version_list = version_list.deepcopy(
            path_prefix=MetadataPath("x/y/z"))

        print(list(version_list.get_versioned_elements()))
        print(list(copied_version_list.get_versioned_elements()))

        # Check the mapping state of the original. It should
        # not have changed.
        self.assertFalse(element_0.mapped)
        self.assertTrue(element_1.mapped)

        original_info = list(version_list.get_versioned_elements())
        copied_info = list(copied_version_list.get_versioned_elements())

        # Check that the number of version list entries matches
        self.assertEqual(len(original_info), len(copied_info))

        # Check that the version list entries match


if __name__ == '__main__':
    unittest.main()
