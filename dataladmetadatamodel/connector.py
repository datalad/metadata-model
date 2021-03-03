from typing import Any, Optional

from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.mapper.reference import Reference


class ConnectedObject:
    def __init__(self):
        self.modified = True

    def is_modified(self) -> bool:
        return self.modified

    def touch(self):
        self.modified = True

    def un_touch(self):
        self.modified = False

    def save(self):
        raise NotImplementedError

    def post_load(self, _family, _realm):
        pass


class Connector:
    def __init__(self,
                 reference: Optional[Reference],
                 obj: Optional[ConnectedObject],
                 is_mapped: bool):
        self.reference = reference
        self.object = obj
        self.is_mapped = is_mapped

    @classmethod
    def from_reference(cls, reference):
        return cls(reference, None, False)

    @classmethod
    def from_object(cls, obj):
        if obj is None:
            return cls.from_reference(
                Reference.get_none_reference())
        return cls(None, obj, True)

    @classmethod
    def from_referenced_object(cls, reference, obj):
        return cls(reference, obj, True)

    def is_object_modified(self) -> bool:
        if self.is_mapped and self.object is not None:
            return self.object.is_modified()
        return False

    def load_object(self) -> Any:
        if not self.is_mapped:
            assert self.reference is not None
            if self.reference.is_none_reference():
                self.object = None
            else:
                self.object = get_mapper(
                    self.reference.mapper_family,
                    self.reference.class_name)(self.reference.realm).map(self.reference)
                self.object.post_load(
                    self.reference.mapper_family,
                    self.reference.realm)
                self.object.un_touch()
            self.is_mapped = True
        return self.object

    def save_object(self) -> Reference:
        """
        Save the connected object, if it is modified and save the
        state of the connector itself.

        Saving the connected object is delegated to the object via
        ConnectedObject.save().
        """
        if self.is_mapped:
            if self.object is None:
                self.reference = Reference.get_none_reference()
            else:
                # If there is no reference yet in this connector
                # or if the object was modified, we have to save it.
                # (There might be no reference here, because the object
                # was already saved through another way.)
                # TODO: can we cache the reference?
                if self.reference is None or self.is_object_modified():
                    self.reference = self.object.save()
        else:
            if self.reference is None:
                self.reference = Reference.get_none_reference()
        return self.reference

    def set(self, obj):
        self.object = obj
        self.reference = None
        self.is_mapped = True

    def purge(self, unsafe: Optional[bool] = False):
        if self.is_object_modified() and unsafe is False:
            raise ValueError(
                f"Cannot purge unsaved, modified object of type "
                f"{type(self.object).__name__}")
        self.object = None
        self.is_mapped = False

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None) -> "Connector":

        """
        Create a copy of the connector. The copied connector
        will be connected to a copy of the original object.
        The connected object will be copied in the following steps:

          1. Loading the original object
          2. Calling deepcopy on the original object to get a copied object
          4. Purging the original object
          3. Creating a connector from the copied object
        """
        if self.is_mapped:
            original_object = self.object
            purge_original = False
        else:
            original_object = self.load_object()
            purge_original = True

        copied_object = original_object.deepcopy(
            new_mapper_family,
            new_realm)

        if purge_original:
            self.purge()

        copied_connector = Connector.from_object(copied_object)
        copied_connector.save_object()
        copied_connector.purge()

        return copied_connector

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"Connector(reference={repr(self.reference)}, "
            f"object={repr(self.object)}, is_mapped={repr(self.is_mapped)})")

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.reference == other.reference
            and self.object == other.object
            and self.is_mapped == other.is_mapped)
