from abc import (
    ABCMeta,
    abstractmethod
)
from typing import (
    Iterable,
    Optional,
)


class ModifiableObject(metaclass=ABCMeta):
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
    def __init__(self, saved_on: Optional[str] = None):
        self.saved_on = set()
        if saved_on:
            self.saved_on.add(saved_on)

    def touch(self):
        self.set_unsaved()

    def set_saved_on(self, destination: str):
        self.saved_on.add(destination)

    def set_unsaved(self):
        self.saved_on = set()

    def is_saved_on(self, destination: str) -> bool:
        """
        Check whether the object is saved on the given
        destination. This check includes whether all
        modifiable sub-objects are saved on the
        given destination.
        """
        if destination not in self.saved_on:
            return False
        return all(
            map(
                lambda element: element.is_saved_on(destination),
                self.get_modifiable_sub_objects()))

    @abstractmethod
    def get_modifiable_sub_objects(self) -> Iterable["ModifiableObject"]:
        raise NotImplementedError
