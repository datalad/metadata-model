import unittest
from unittest.mock import patch

from ..reference import Reference


class TestReference(unittest.TestCase):

    def check_json_values(self, json_object):
        for value in json_object.values():
            if isinstance(value, (dict, list)):
                self.check_json_values(value)
            else:
                self.assertIsInstance(value, (str, int, float))

    def test_json_serialisation(self):
        reference = Reference("SomeClass", "some-location")
        json_object = reference.to_json_obj()
        self.check_json_values(json_object)
        self.assertEqual(json_object["class_name"], "SomeClass")
        self.assertEqual(json_object["location"], "some-location")

    def test_json_serialisation_deserialization(self):
        reference1 = Reference("SomeClass", "some-location")
        json_object = reference1.to_json_obj()
        reference2 = Reference.from_json_obj(json_object)
        self.assertEqual(reference1, reference2)

    def test_old_style_warning(self):
        reference1 = Reference("SomeClass", "some-location")

        json_object = reference1.to_json_obj()
        json_object["mapper_family"] = "git"
        json_object["realm"] = "/tmp/t"

        with patch("dataladmetadatamodel.mapper.reference.logger") as logger:
            reference2 = Reference.from_json_obj(json_object)
            self.assertEqual(reference1, reference2)
            logger.info.assert_called_once()

    def test_remote(self):
        for realm in ("git:x.com", "http://x.com/", "https://x.com/", "ssh:x@x.com"):
            self.assertTrue(Reference.is_remote(realm))
            self.assertFalse(Reference.is_local(realm))

    def test_local(self):
        for realm in ("a/b/c", "C:\\x", "c:\\x", "/a/b/c"):
            self.assertFalse(Reference.is_remote(realm))
            self.assertTrue(Reference.is_local(realm))


if __name__ == '__main__':
    unittest.main()
