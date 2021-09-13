from abc import (
    ABCMeta,
    abstractmethod
)
from typing import Optional

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.mapper.xxx import get_mapper
from dataladmetadatamodel.mapper.reference import Reference


class Mapper(metaclass=ABCMeta):
    """
    Mapper are responsible for populating an existing
    object of a certain class from a backend. The mapper
    will delegate sub-object mapping to the mapper for
    the class of the sub-object.

    This base class handles default destination
    """
    def __init__(self, class_name: str, default_destination: Optional[str] = None):
        self.class_name = class_name
        self.destination = default_destination

    def read_in(self, mappable_object: MappableObject, reference: Reference):
        assert type(mappable_object).__name__ == self.class_name
        assert reference.class_name == self.class_name
        return self.read_in_impl(mappable_object, reference)

    def write_out(self,
                  mappable_object: MappableObject,
                  destination: Optional[str] = None
                  ) -> Reference:

        if destination is None:
            if self.destination is None:
                raise Exception("'destination' not set and no default destination provided")
            destination = self.destination
        return self.write_out_impl(mappable_object, destination)

    @abstractmethod
    def read_in_impl(self, mappable_object: MappableObject, reference: Reference):
        raise NotImplementedError

    @abstractmethod
    def write_out_impl(self, mappable_object: MappableObject, destination: str) -> Reference:
        raise NotImplementedError
