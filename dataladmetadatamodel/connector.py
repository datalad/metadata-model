from typing import Any, Optional

from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.mapper.reference import Reference


class ConnectedObject:
    def pre_save(self, _family, _realm):
        pass

    def post_load(self, _family, _realm):
        pass


class Connector:
    def __init__(self,
                 reference: Optional[Reference],
                 obj: ConnectedObject,
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

    def load_object(self, family, realm) -> Any:     # TODO: rename to load_object
        if not self.is_mapped:
            assert self.reference is not None
            self.object = get_mapper(
                self.reference.mapper_family,
                self.reference.class_name)(realm).map(self.reference)
            self.object.post_load(family, realm)
            self.is_mapped = True
        return self.object

    def save_object(self, family, realm, force_write=False) -> Reference:   # TODO: rename to save_object
        if self.is_mapped:
            if self.is_modified or force_write:
                class_name = type(self.object).__name__
                self.object.pre_save(family, realm)
                self.reference = Reference(
                    family,
                    class_name,
                    get_mapper(
                        family,
                        class_name
                    )(realm).unmap(self.object)
                )
                self.is_modified = False
            return self.reference
        raise ValueError("No object is loaded or set")

    def set(self, obj):
        self.object = obj
        self.reference = None
        self.is_mapped = True
        self.is_modified = True

    def purge(self):
        if self.is_mapped and self.is_modified:
            raise ValueError("Cannot purge unsaved modified object")
        self.object = None
        self.is_mapped = None
        self.is_modified = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"Connector(reference={repr(self.reference)}, "
            f"obj={repr(self.object)}, is_mapped={repr(self.is_mapped)}, "
            f"is_modified={self.is_modified})")
