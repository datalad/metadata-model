from abc import (
    ABCMeta,
    abstractmethod
)
from typing import (
    Iterable,
    Optional
)

from dataladmetadatamodel.log import logger
from dataladmetadatamodel.modifiableobject import ModifiableObject
from dataladmetadatamodel.mapper.reference import Reference


class MappableObject(ModifiableObject, metaclass=ABCMeta):
    """
    Base class for objects that can be mapped onto a
    storage backend.
    """
    def __init__(self,
                 reference: Optional[Reference] = None):
        """
        Create a mappable object with a reference or None.
        If the reference is given, we assume that the object
        is saved on the respective realm, and that it is
        not modified.

        We also assume that an object that is created with
        a reference is not mapped. That means it has to be
        read in before operating on its elements.

        Generally unmapped objects are expected to be
        unmodified.
        """
        assert isinstance(reference, (type(None), Reference))

        # We assume that objects that carry a reference
        # have been saved on the realm in the reference.
        # That also means that they are not modified
        super().__init__(
            reference.realm
            if reference is not None and not reference.is_none_reference()
            else None
        )

        self.reference = reference
        self.mapper_private_data = dict()
        self.mapped = reference is None
        assert isinstance(reference, (type(None), Reference)), \
            f"object {self} initialized with invalid reference: {reference}"

    def get_modifiable_sub_objects(self) -> Iterable["MappableObject"]:
        """
        Mappable objects might be mapped (in memory) or not mapped
        (stored on secondary storage and purged in order to consume
        as little memory as possible).
        If on abject is not mapped, we assume that it is not modified
        because modifying means: "read-in", "modify", "write-out", and
        "purge". Since "purge" will only succeed if the object was
        written out.
        """
        if not self.mapped:
            return []

        # delegate to our subclasses
        return self.get_modifiable_sub_objects_impl()

    def read_in(self,
                backend_type="git") -> "MappableObject":

        from dataladmetadatamodel.mapper import get_mapper

        if self.mapped is False:

            assert self.reference is not None

            # if the reference is a None-reference,
            # we can handle this here
            if self.reference.is_none_reference():
                assert self.reference.class_name == type(self).__name__
                logger.warning(f"read_in({self}): None-reference in {self}")
                self.purge_impl()
                return self

            # ensure that the object is save on the given realm
            if not self.is_saved_on(self.reference.realm):
                logger.error(
                    f"read_in({self}): trying to overwrite a modified object")
                raise RuntimeError(
                    "read_in({self}): tried to read over a modified object")

            # the object is not mapped, but saved on reference.realm,
            # use the mappable object-specific mapper to read
            # the object in.
            get_mapper(
                type(self).__name__,
                backend_type).map_in(
                    self,
                    self.reference)

            # Mark the object as mapped.
            self.mapped = True

        else:

            logger.debug(
                f"read_in({self}): not needed, object is already mapped")

        return self

    def write_out(self,
                  destination: Optional[str] = None,
                  backend_type: str = "git",
                  force_write: bool = False) -> Reference:

        from dataladmetadatamodel.mapper import get_mapper

        # if the object is not mapped and not modified,
        # we do not have to do anything.
        if not self.mapped:
            assert isinstance(self.reference, Reference), \
                f"write_out: object {self} has no valid " \
                f"reference: {self.reference}"

            if not self.is_saved_on(destination):
                if self.reference.is_none_reference():
                    logger.debug(
                        f"write_out({self}): not possible, because object "
                        f" has a None-reference: {self.reference}")
                    return self.reference

                raise RuntimeError(
                    f"write_out({self}): modified object got lost "
                    f"on {destination}")

            logger.debug(
                f"write_out({self}): not needed, object already"
                f" saved on {destination}")
            return self.reference

        if self.reference and not self.reference.is_none_reference():
            destination = destination or self.reference.realm
        assert destination is not None, \
            f"write_out({self}): no destination available for {self}"

        if self.is_saved_on(destination):
            if not force_write:
                logger.debug(
                    f"write_out({self}): skipping map_out because {self} "
                    f"is already stored on {destination}")
                return self.reference

            logger.debug(
                f"write_out({self}): forcing map_out, although {self} "
                f"is already stored on {destination}")

        logger.debug(
            f"write_out({self}): calling map_out to save {self} "
            f"to {destination}")

        self.reference = get_mapper(
            type(self).__name__,
            backend_type).map_out(
                self,
                destination,
                force_write)

        self.set_saved_on(destination)

        assert isinstance(self.reference, Reference), \
            f"write_out({self}): object {self} has no valid " \
            f"reference: {self.reference}"

        return self.reference

    def purge(self):
        if self.mapped:

            if len(self.saved_on) == 0:
                raise ValueError(
                    f"purge({self}): called with unsaved object: {self}")

            self.purge_impl()
            self.mapped = False

    def ensure_mapped(self,
                      backend_type="git") -> bool:
        if not self.mapped:
            self.read_in(backend_type)
            return True
        return False

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_destination: Optional[str] = None,
                 **kwargs) -> "MappableObject":

        needs_purge = self.ensure_mapped()

        result = self.deepcopy_impl(new_mapper_family,
                                    new_destination,
                                    **kwargs)

        if needs_purge is True:
            self.purge()

        return result

    @abstractmethod
    def get_modifiable_sub_objects_impl(self) -> Iterable["MappableObject"]:
        raise NotImplementedError

    @abstractmethod
    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "MappableObject":
        raise NotImplementedError

    @abstractmethod
    def purge_impl(self):
        raise NotImplementedError
