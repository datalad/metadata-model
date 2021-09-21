from typing import (
    Iterable,
    List,
    Optional
)
import unittest

from dataladmetadatamodel.modifiableobject import ModifiableObject


destination = "/tmp/t"


class SUTModifiableObject(ModifiableObject):
    def __init__(self, saved_on: Optional[str] = None):
        super().__init__()
        if saved_on is not None:
            self.set_saved_on(saved_on)
        self.something = "Something " * 100

    def get_modifiable_sub_objects(self) -> Iterable:
        return []


class TestModifiableObject(unittest.TestCase):

    def test_new_clean(self):
        mo = SUTModifiableObject()
        self.assertFalse(mo.is_saved_on(destination))

    def test_touching_cleaning(self):
        mo = SUTModifiableObject()
        self.assertFalse(mo.is_saved_on(destination))
        mo.set_saved_on(destination)
        self.assertTrue(mo.is_saved_on(destination))

    def test_sub_object_modification(self):
        class Bag(ModifiableObject):
            def __init__(self, _sub_objects: List[ModifiableObject]):
                super().__init__()
                self.sub_objects = _sub_objects

            def get_modifiable_sub_objects(self) -> Iterable[ModifiableObject]:
                return self.sub_objects

        sub_objects = [SUTModifiableObject(destination) for _ in range(3)]

        bag = Bag(sub_objects)
        bag.set_saved_on(destination)

        self.assertTrue(bag.is_saved_on(destination), f"Expected complete bag is saved on {destination}")

        sub_objects[0].touch()
        self.assertFalse(bag.is_saved_on(destination), f"Expected modified bag is not saved on {destination}")


if __name__ == '__main__':
    unittest.main()
