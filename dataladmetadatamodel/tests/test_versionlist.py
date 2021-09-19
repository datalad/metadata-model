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

        path_prefix = "x/y/z"
        copied_version_list = version_list.deepcopy(
            path_prefix=MetadataPath(path_prefix))

        print(list(version_list.get_versioned_elements()))
        print(list(copied_version_list.get_versioned_elements()))

        # Check that the mapping state of the original
        # has not changed.
        self.assertFalse(element_0.mapped)
        self.assertTrue(element_1.mapped)

        # Check that the copied elements are unmapped
        for _, (_, _, copied_dummy) in copied_version_list.get_versioned_elements():
            self.assertFalse(copied_dummy.mapped)

        for primary_version, (_, path, dummy) in version_list.get_versioned_elements():
            expected_path = path_prefix / path
            _, copy_path, copied_dummy = copied_version_list.get_versioned_element(primary_version)
            self.assertEqual(expected_path, copy_path)
            self.assertEqual(copied_dummy.copied_from, dummy)


if __name__ == '__main__':
    unittest.main()


# TODO: ensure that copies are unmapped.
#  That means, after:
#  copied_object = original_object.deepcopy(backend_type, destination)
#  is executed, the copied_object is unmapped.


# TODO: unify purge behaviour.
#  For example: UUIDSet keeps the dictionary of VersionLists when purged,
#  but VersionList