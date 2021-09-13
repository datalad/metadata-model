from typing import Iterable


class ModifiableObject:
    """
    Modifiable objects track their modification status.
    including the modification status of potential
    contained objects.

    If one of the contained objects is modified, the
    containing object is considered modified as well.

    Objects determine their modification-relevant
    sub-objects by implementing their version of the
    method "get_modifiable_sub_objects".
    """
    def __init__(self):
        # A modifiable object is assumed
        # to be unmodified upon creation
        self.dirty = False

    def touch(self):
        self.dirty = True

    def clean(self):
        self.dirty = False

    def is_modified(self) -> bool:
        """
        Determine whether the object or one of its contained
        objects was modified.
        """
        if not self.dirty:
            self.dirty = self._sub_objects_modified()
        return self.dirty

    def _sub_objects_modified(self):
        return any(map(lambda element: element.is_modified(), self.get_modifiable_sub_objects()))

    def get_modifiable_sub_objects(self) -> Iterable["ModifiableObject"]:
        return []
