import unittest
from typing import Union

from ..mapper import Mapper
from ..reference import Reference
from ...datasettree import DatasetTree
from ...filetree import FileTree
from ...mappableobject import MappableObject


class DummyMapper(Mapper):
    def __init__(self,
                 class_name: str,
                 destination: str,
                 location: str):

        super().__init__(class_name, destination)
        self.location = location
        self.map_in_call_count = 0

    def map_in_impl(self,
                    mappable_object: MappableObject,
                    realm: str,
                    reference: Reference) -> None:
        self.map_in_call_count += 1
        return

    def map_out_impl(self,
                     mappable_object: MappableObject,
                     realm: str,
                     force_write: bool
                     ) -> Reference:
        return Reference(self.class_name,
                         self.location)


class TestMapper(unittest.TestCase):

    def _test_compatibility_tree(self,
                                tree_class: Union[type(DatasetTree), type(FileTree)]):
        mapper = DummyMapper("MTreeNode", "/tmp/1", "loc-1")
        tree = tree_class()
        mapper.map_in(tree,
                      "/tmp/1",
                      Reference(tree_class.__name__,
                                "location0"))
        self.assertEqual(mapper.map_in_call_count, 1)

    def test_compatibility_datasettree(self):
        self._test_compatibility_tree(DatasetTree)

    def test_compatibility_filetree(self):
        self._test_compatibility_tree(FileTree)


if __name__ == '__main__':
    unittest.main()
