import json
import unittest
from unittest import mock

from .... import version_string
from ...reference import Reference
from ..referencemapper import ReferenceGitMapper


test_realm_name = "ewkd0iasd"
location_0 = "a000000000000000000"


class TestVersionListMapper(unittest.TestCase):

    def test_basic_unmapping(self):
        with mock.patch(
                "dataladmetadatamodel.mapper.gitmapper"
                ".referencemapper.git_save_str") as save:

            save.configure_mock(return_value=location_0)

            none_reference = Reference.get_none_reference()
            ReferenceGitMapper(test_realm_name).unmap(none_reference)
            representation = save.call_args[0][1]
            self.assertEqual(
                json.loads(representation),
                {
                    "@": {
                        "type": "Reference",
                        "version": version_string
                    },
                    "mapper_family": "*None*",
                    "realm": "*None*",
                    "class_name": "*None*",
                    "location": "*None*"
                })

    def test_none_reference_mapping(self):

        with mock.patch("dataladmetadatamodel.mapper.gitmapper.referencemapper.git_load_str") as load:

            load.return_value = json.dumps({
                "@": {
                    "type": "Reference",
                    "version": version_string
                },
                "mapper_family": "*None*",
                "realm": "*None*",
                "class_name": "*None*",
                "location": "*None*"
            })

            loaded_ref = ReferenceGitMapper(test_realm_name).map(
                Reference(
                    "git",
                    test_realm_name,
                    "Reference",
                    "ignored due to patch"))
            self.assertTrue(loaded_ref.is_none_reference())


if __name__ == '__main__':
    unittest.main()
