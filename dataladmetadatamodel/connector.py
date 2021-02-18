from typing import Any, Optional

from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.mapper.reference import Reference, none_class_name, none_location


class ConnectedObject:
    def pre_save(self, _family, _realm):
        pass

    def post_load(self, _family, _realm):
        pass


class Connector:
    def __init__(self,
                 reference: Optional[Reference],
                 obj: Optional[ConnectedObject],
                 is_mapped: bool,
                 is_modified: bool):
        self.reference = reference
        self.object = obj
        self.is_mapped = is_mapped
        self.is_modified = is_modified

    @classmethod
    def from_reference(cls, reference):
        return cls(reference, None, False, False)

    @classmethod
    def from_object(cls, obj):
        return cls(None, obj, True, True)

    @classmethod
    def from_referenced_object(cls, reference, obj):
        return cls(reference, obj, True, False)

    def load_object(self, mapper_family, realm) -> Any:
        if not self.is_mapped:
            assert self.reference is not None
            if self.reference.is_none_reference():
                self.object = None
            else:
                self.object = get_mapper(
                    self.reference.mapper_family,
                    self.reference.class_name)(realm).map(self.reference)
                self.object.post_load(mapper_family, realm)
            self.is_mapped = True
        return self.object

    def save_object(self, mapper_family, realm, force_write=False) -> Reference:
        if self.is_mapped:
            if self.is_modified or force_write:
                class_name = type(self.object).__name__
                self.object.pre_save(mapper_family, realm)
                self.reference = Reference(
                    mapper_family,
                    realm,
                    class_name,
                    get_mapper(
                        mapper_family,
                        class_name
                    )(realm).unmap(self.object)
                )
                self.is_modified = False
        else:
            if self.reference is None:
                self.reference = Reference.get_none_reference(
                    mapper_family,
                    realm)
        return self.reference

    def set(self, obj):
        self.object = obj
        self.reference = None
        self.is_mapped = True
        self.is_modified = True

    def purge(self):
        if self.is_mapped and self.is_modified:
            raise ValueError("Cannot purge unsaved modified object")
        self.object = None
        self.is_mapped = False
        self.is_modified = False

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
            original_object = self.load_object(
                self.reference.mapper_family,
                self.reference.realm)
            purge_original = True

        copied_object = original_object.deepcopy(
            new_mapper_family,
            new_realm)

        if purge_original:
            self.purge()

        new_mapper_family = new_mapper_family or self.reference.mapper_family
        new_realm = new_realm or self.reference.realm

        copied_connector = Connector.from_object(copied_object)
        copied_connector.save_object(new_mapper_family, new_realm)
        copied_connector.purge()

        return copied_connector

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"Connector(reference={repr(self.reference)}, "
            f"object={repr(self.object)}, is_mapped={repr(self.is_mapped)}, "
            f"is_modified={self.is_modified})")

    def __eq__(self, other):
        return (
            type(self) == type(other)
            and self.reference == other.reference
            and self.object == other.object
            and self.is_mapped == other.is_mapped
            and self.is_modified == other.is_modified)
