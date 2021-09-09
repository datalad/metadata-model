from abc import (
    ABCMeta,
    abstractmethod
)
from typing import (
    Any,
    Dict,
    Optional
)

from dataladmetadatamodel.mapper.reference import Reference
from dataladmetadatamodel.log import logger


MAPPED_OBJECTS: Dict[id, Reference] = dict()


class BaseMapper(metaclass=ABCMeta):
    """
    Base class for mapper classes

    Mapper classes are responsible for retrieving
    an object based on a reference and for persisting
    an object and returning a reference to the
    persisted object
    """

    def __init__(self, realm: Optional[str] = None):
        """
        realm defines the storage container for
        the elements that are mapped. Currently
        a model_old instance can only be stored in
        a single container, i.e. all objects of
        the model_old are stored in the same container,
        although different parts may be present
        in memory at different times.
        """
        self.realm = realm

    def map(self, reference: Reference) -> Any:
        obj = self.map_impl(reference)
        MAPPED_OBJECTS[id(obj)] = reference
        return obj

    def unmap(self, obj) -> Reference:
        key = (id(obj), type(obj).__name__)
        if key in MAPPED_OBJECTS:
            logger.warning(f"object of {type(obj).__name__} at {id(obj)} already saved")
        else:
            reference = self.unmap_impl(obj)
            MAPPED_OBJECTS[key] = reference
        return MAPPED_OBJECTS[key]

    @abstractmethod
    def map_impl(self, reference: Reference) -> Any:
        raise NotImplementedError

    @abstractmethod
    def unmap_impl(self, obj) -> Reference:
        raise NotImplementedError

    @staticmethod
    def start_mapping_cycle():
        global MAPPED_OBJECTS
        MAPPED_OBJECTS = dict()
