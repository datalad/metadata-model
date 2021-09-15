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

        if reference is None:
            # if no reference is given, we assume a newly
            # created object, and set the modified state.
            self.mapped = True
            self.touch()
        else:
            self.mapped = False

    def read_in(self, backend_type="git") -> "MappableObject":
        from dataladmetadatamodel.mapper.xxx import get_mapper

        if self.mapped is False:
            assert self.reference is not None
            get_mapper(
                type(self).__name__,
                backend_type).map_in(self, self.reference)
            self.mapped = True
            self.clean()
        return self

    def write_out(self,
                  destination: Optional[str] = None,
                  backend_type: str = "git",
                  force_write: bool = False) -> Reference:

        from dataladmetadatamodel.mapper.xxx import get_mapper

        if self.mapped:
            if not self.is_modified() and not force_write:
                logger.debug(
                    "write_out: skipping map_out because "
                    "object is not modified.")
            else:
                destination = destination or self.reference.realm
                assert destination is not None, f"No destination provided for {self}"
                self.reference = get_mapper(
                    type(self).__name__,
                    backend_type).map_out(self, destination, force_write)
                self.clean()

        assert self.reference is not None
        return self.reference

    def purge(self, force: bool = False):
        if self.mapped:
            if self.is_modified():
                if not force:
                    raise ValueError(f"Trying to purge a modified object: {self}")
                logger.warning(f"Forcefully purging modified object: {self}")
            self.purge_impl(force)
            self.mapped = False
            self.clean()

    @abstractmethod
    def purge_impl(self, force: bool):
        raise NotImplementedError
