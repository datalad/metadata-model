import unittest

from ..reference import Reference


class TestReference(unittest.TestCase):

    def check_json_values(self, json_object):
        for value in json_object.values():
            if isinstance(value, (dict, list)):
                self.check_json_values(value)
            else:
                self.assertIsInstance(value, (str, int, float))

    def test_json_serialisation(self):
        reference = Reference("git", "/tmp/t1", "SomeClass", "some-location")
        json_object = reference.to_json_obj()
        self.check_json_values(json_object)


if __name__ == '__main__':
    unittest.main()
