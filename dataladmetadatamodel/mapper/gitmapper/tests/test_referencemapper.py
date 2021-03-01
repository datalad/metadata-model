import unittest
from unittest import mock

from ...reference import Reference
from ..referencemapper import ReferenceGitMapper


test_realm_name = "ewkd0iasd"


class MyTestCase(unittest.TestCase):

    def test_none_reference_handling(self):
        with mock.patch("dataladmetadatamodel.mapper.gitmapper.referencemapper.git_save_str") as save:

            none_reference = Reference.get_none_reference("git", test_realm_name)
            ReferenceGitMapper(test_realm_name).unmap(none_reference)
            self.assertEqual(
                save.call_args,
                mock.call(
                    test_realm_name,
                    '{"@": {"type": "Reference", "version": "1.0"}, "mapper_family": "git", "realm": "ewkd0iasd", "class_name": "*None*", "location": "*None*"}'))


if __name__ == '__main__':
    unittest.main()
