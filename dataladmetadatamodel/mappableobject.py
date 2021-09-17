from abc import (
    ABCMeta,
    abstractmethod
)
from typing import Optional

from dataladmetadatamodel.log import logger
from dataladmetadatamodel.modifiableobject import ModifiableObject
from dataladmetadatamodel.mapper.reference import Reference


class MappableObject(ModifiableObject, metaclass=ABCMeta):
    """
    Base class for objects that can
    be mapped onto a storage backend
    """
    def __init__(self, reference: Optional[Reference] = None):
        super().__init__()
        self.reference = reference
        self.mapper_private_data = dict()
        self.mapped = reference is None
        assert isinstance(reference, (type(None), Reference)), f"object {self} initialized with invalid reference: {reference}"

    def read_in(self, backend_type="git") -> "MappableObject":
        from dataladmetadatamodel.mapper import get_mapper

        if self.mapped is False:
            assert self.reference is not None
            get_mapper(
                type(self).__name__,
                backend_type).map_in(self, self.reference)
            self.mapped = True
            self.set_saved_on(self.reference.realm)
        return self

    def write_out(self,
                  destination: Optional[str] = None,
                  backend_type: str = "git",
                  force_write: bool = False) -> Reference:

        from dataladmetadatamodel.mapper import get_mapper

        if not self.mapped:
            assert isinstance(self.reference, Reference), f"write_out: object {self} has no valid reference: {self.reference}"
            return self.reference

        if self.reference:
            destination = destination or self.reference.realm
        assert destination is not None, f"write_out: no destination available for {self}"

        if self.is_saved_on(destination):
            if force_write:
                logger.debug(
                    f"write_out: forcing map_out, {self} "
                    f"is already stored on {destination}")
            else:
                logger.debug(
                    f"write_out: skipping map_out because {self} "
                    f"is already stored on {destination}")
        else:
            logger.debug(
                f"write_out: calling map_out to save {self} to {destination}")
            self.reference = get_mapper(
                type(self).__name__,
                backend_type).map_out(self, destination, force_write)
            self.set_saved_on(destination)
        assert isinstance(self.reference, Reference), f"write_out: object {self} has no valid reference: {self.reference}"
        return self.reference

    def purge(self, force: bool = False):
        if self.mapped:
            if len(self.saved_on) == 0:
                if not force:
                    raise ValueError(f"purge: called with unsaved object: {self}")
                logger.warning(f"Forcefully purging unsaved object: {self}")
            self.purge_impl(force)
            self.mapped = False
            self.set_unsaved()

    @abstractmethod
    def purge_impl(self, force: bool):
        raise NotImplementedError
