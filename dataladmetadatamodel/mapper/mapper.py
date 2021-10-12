from abc import (
    ABCMeta,
    abstractmethod
)
from typing import Optional

from dataladmetadatamodel.log import logger
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
               mappable_object: "MappableObject",
               realm: str,
               reference: Reference) -> None:

        # Check for old-style file tree and dataset tree references
        if reference.class_name in ("FileTree", "DatasetTree"):
            logger.warning(f"Mapper.map_in(): converting reference to class "
                           f"{reference.class_name} to a reference to class "
                           f"MTreeNode")
            reference.class_name = "MTreeNode"

        # TODO: this is not too nice, but required since FileTree and
        #  DatasetTree are proxies for MTreeNode which just add some
        #  methods.
        mo_class_name = type(mappable_object).__name__
        if mo_class_name in ("FileTree", "DatasetTree"):
            assert self.class_name == "MTreeNode", \
                f"Mappable object class: {mo_class_name} " \
                f"can not be mapped in by a mapper for class: {self.class_name}"
        else:
            assert mo_class_name == self.class_name, \
                f"Mappable object class name ({mo_class_name}) " \
                f"does not match this mapper's class_name ({self.class_name})"

        assert reference.class_name == self.class_name, \
            f"Reference class name ({reference.class_name}) " \
            f"does not match self.class_name ({self.class_name})"

        self.map_in_impl(mappable_object, realm, reference)

    def map_out(self,
                mappable_object: "MappableObject",
                realm: Optional[str] = None,
                force_write: bool = False) -> Reference:

        if realm is None:
            if self.destination is None:
                raise Exception(
                    "'destination' not set and no default destination provided")
            realm = self.destination
        return self.map_out_impl(mappable_object, realm, force_write)

    @abstractmethod
    def map_in_impl(self,
                    mappable_object: "MappableObject",
                    realm: str,
                    reference: Reference) -> None:
        raise NotImplementedError

    @abstractmethod
    def map_out_impl(self,
                     mappable_object: "MappableObject",
                     realm: str,
                     force_write: bool) -> Reference:
        raise NotImplementedError
