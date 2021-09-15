import unittest
from typing import Iterable
from unittest.mock import MagicMock

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.mapper.xxx import set_mapper


class SUTMappableObject(MappableObject):
    def __init__(self, reference=None):
        super().__init__(reference)
        self.something = "Something " * 100

    def purge_impl(self, force: bool):
        self.something = None

    def get_modifiable_sub_objects(self) -> Iterable:
        return []


class TestMappableObject(unittest.TestCase):

    def setUp(self) -> None:
        self.test_mapper = MagicMock()
        set_mapper("SUTMappableObject", "git", self.test_mapper)

    def test_new_mapped(self):
        # expect that a newly created object without reference is written out once
        mo = SUTMappableObject(None)
        mo.write_out("/tmp/t", "git")
        self.test_mapper.map_out.assert_called_once_with(mo, "/tmp/t", False)
        mo.write_out("/tmp/t", "git")
        self.test_mapper.map_out.assert_called_once_with(mo, "/tmp/t", False)

    def test_purge(self):
        mo = SUTMappableObject(None)
        self.assertRaises(ValueError, mo.purge)
        mo.write_out("/tmp/t", "git")
        mo.purge()
        self.test_mapper.map_out.assert_called_once_with(mo, "/tmp/t", False)

    def test_forced_purge(self):
        mo = SUTMappableObject(None)
        mo.purge(force=True)
        self.test_mapper.map_out.assert_not_called()


if __name__ == '__main__':
    unittest.main()
