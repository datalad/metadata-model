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
        return self.map_impl(reference)

    def unmap(self, obj) -> Reference:
        return self.unmap_impl(obj)

    @abstractmethod
    def map_impl(self, reference: Reference) -> Any:
        raise NotImplementedError

    @abstractmethod
    def unmap_impl(self, obj) -> Reference:
        raise NotImplementedError
