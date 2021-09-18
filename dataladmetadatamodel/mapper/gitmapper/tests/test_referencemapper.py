import json
import unittest
from unittest import mock

from .... import version_string
from ...reference import Reference
from ..referencemapper import ReferenceGitMapper


test_realm_name = "ewkd0iasd"
location_0 = "a000000000000000000000000000000000000000"


class TestReferenceMapper(unittest.TestCase):

    def test_none_reference_unmapping(self):
        with mock.patch("dataladmetadatamodel.mapper.gitmapper.referencemapper.git_save_json") as save:

            save.return_value = location_0

            reference_to_map_out = Reference.get_none_reference("some class")
            reference = ReferenceGitMapper("Reference").map_out_impl(
                reference_to_map_out,
                test_realm_name,
                False)

            representation = save.call_args[0][1]
            self.assertEqual(
                representation,
                {
                    "@": {"type": "Reference", "version": version_string},
                    "mapper_family": "*None*",
                    "realm": "*None*",
                    "class_name": "some class",
                    "location": "*None*"
                }
            )

    def test_none_reference_mapping(self):

        with mock.patch("dataladmetadatamodel.mapper.gitmapper.referencemapper.git_load_json") as load:
            load.return_value = {
                "@": {"type": "Reference", "version": version_string},
                "mapper_family": "*None*",
                "realm": "*None*",
                "class_name": "*None*",
                "location": "*None*"
            }

            reference_to_map_in = Reference("", "", "", "")
            ReferenceGitMapper("Reference").map_in_impl(
                reference_to_map_in,
                Reference("git", "somename", "Reference", "ignored due to patch"))
            self.assertTrue(reference_to_map_in.is_none_reference())


if __name__ == '__main__':
    unittest.main()
