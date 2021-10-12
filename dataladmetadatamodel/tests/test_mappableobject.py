import unittest
from typing import (
    Iterable,
    Optional
)
from unittest.mock import MagicMock

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.mapper import set_mapper
from dataladmetadatamodel.mapper.reference import Reference


class SUTMappableObject(MappableObject):
    def __init__(self,
                 realm=None,
                 reference=None):

        super().__init__(realm, reference)
        self.something = "Something " * 100

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "MappableObject":
        return self

    def purge_impl(self):
        self.something = None

    def get_modifiable_sub_objects_impl(self) -> Iterable:
        return []


class TestMappableObject(unittest.TestCase):

    def setUp(self) -> None:
        self.test_mapper = MagicMock(
            map_out=MagicMock(return_value=Reference(
                "SUTMappableObject",
                "location:00001111"
            ))
        )
        set_mapper("SUTMappableObject", "git", self.test_mapper)

    def test_new_mapped(self):
        # expect that a newly created object without reference is written out once
        mo = SUTMappableObject()
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

    def test_purge_unsaved(self):
        mo = SUTMappableObject(None)
        self.assertRaises(ValueError, mo.purge)


if __name__ == '__main__':
    unittest.main()
