import unittest
from unittest import mock
from uuid import UUID


location_0 = "a000000000000000000000000000000000000000"
location_1 = "a000000000000000000000000000000000000001"

uuid_0 = UUID("00000000000000000000000000000000")
uuid_1 = UUID("00000000000000000000000000000001")


expected_tree_args = {
    ('100644', 'blob', 'a000000000000000000000000000000000000001', '00000000-0000-0000-0000-000000000001'),
    ('100644', 'blob', 'a000000000000000000000000000000000000001', '00000000-0000-0000-0000-000000000000')
}


class TestUUIDSetMapper(unittest.TestCase):

    def test_basic_unmapping(self):
        from dataladmetadatamodel.uuidset import UUIDSet
        from dataladmetadatamodel.versionlist import VersionList

        with mock.patch("dataladmetadatamodel.mapper.gitmapper.uuidsetmapper.git_save_tree") as save_tree, \
                mock.patch("dataladmetadatamodel.mapper.gitmapper.uuidsetmapper.git_update_ref") as update_ref, \
                mock.patch("dataladmetadatamodel.mapper.gitmapper.versionlistmapper.git_save_json") as save_json:

            save_tree.configure_mock(return_value=location_0)
            save_json.configure_mock(return_value=location_1)

            uuid_set = UUIDSet({
                uuid_0: VersionList(),
                uuid_1: VersionList()
            })

            uuid_set.write_out("/tmp/t1")

            tree_args = save_tree.call_args[0][1]
            self.assertEqual(tree_args, expected_tree_args)


if __name__ == '__main__':
    unittest.main()
