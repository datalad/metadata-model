from typing import (
    Iterable,
    List
)
import unittest

from dataladmetadatamodel.modifiableobject import ModifiableObject


class SUTModifiableObject(ModifiableObject):
    def __init__(self):
        super().__init__()
        self.something = "Something " * 100

    def get_modifiable_sub_objects(self) -> Iterable:
        return []


class TestModifiableObject(unittest.TestCase):

    def test_new_clean(self):
        mo = SUTModifiableObject()
        self.assertFalse(mo.is_modified())

    def test_touching_cleaning(self):
        mo = SUTModifiableObject()
        mo.touch()
        self.assertTrue(mo.is_modified())
        mo.clean()
        self.assertFalse(mo.is_modified())

    def test_sub_object_modification(self):
        class Bag(ModifiableObject):
            def __init__(self, sub_objects: List[ModifiableObject]):
                super().__init__()
                self.sub_objects = sub_objects

            def get_modifiable_sub_objects(self) -> Iterable[ModifiableObject]:
                return self.sub_objects

        sub_objects = [SUTModifiableObject() for _ in range(3)]

        bag = Bag(sub_objects)
        self.assertFalse(bag.is_modified(), "Expected un-modified state due to newly instantiated sub-objects")

        sub_objects[0].touch()
        self.assertTrue(bag.is_modified(), "Expected modified state due to one modified sub-object")


if __name__ == '__main__':
    unittest.main()
