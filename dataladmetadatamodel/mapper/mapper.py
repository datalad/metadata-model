from abc import (
    ABCMeta,
    abstractmethod
)
from typing import Optional

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.mapper.reference import Reference


class Mapper(metaclass=ABCMeta):
    """
    Mapper are responsible for populating an existing
    object of a certain class from a backend. The mapper
    will delegate sub-object mapping to the mapper for
    the class of the sub-object.

    This base class handles default destination
    """
    def __init__(self,
                 class_name: str,
                 default_destination: Optional[str] = None):
        self.class_name = class_name
        self.destination = default_destination

    def map_in(self,
               mappable_object: MappableObject,
               reference: Reference) -> None:

        assert type(mappable_object).__name__ == self.class_name
        assert reference.class_name == self.class_name
        self.map_in_impl(mappable_object, reference)

    def map_out(self,
                mappable_object: MappableObject,
                destination: Optional[str] = None,
                force_write: bool = False) -> Reference:

        if destination is None:
            if self.destination is None:
                raise Exception(
                    "'destination' not set and no default destination provided")
            destination = self.destination
        return self.map_out_impl(mappable_object, destination, force_write)

    @abstractmethod
    def map_in_impl(self,
                    mappable_object: MappableObject,
                    reference: Reference) -> None:
        raise NotImplementedError

    @abstractmethod
    def map_out_impl(self,
                     mappable_object: MappableObject,
                     destination: str,
                     force_write: bool) -> Reference:
        raise NotImplementedError
