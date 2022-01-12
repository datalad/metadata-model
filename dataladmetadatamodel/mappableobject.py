from abc import (
    ABCMeta,
    abstractmethod,
)
from contextlib import contextmanager
from typing import (
    Iterable,
    Optional,
)

from dataladmetadatamodel.log import logger
from dataladmetadatamodel.modifiableobject import ModifiableObject
from dataladmetadatamodel.mapper.reference import Reference


@contextmanager
def ensure_mapped(mappable_object):
    needs_purge = False
    try:
        if mappable_object is not None:
            needs_purge = mappable_object.ensure_mapped()
        yield mappable_object
    finally:
        if needs_purge:
            mappable_object.purge()


class MappableObject(ModifiableObject, metaclass=ABCMeta):
    """
    Base class for objects that can be mapped onto a
    storage backend.
    """
    def __init__(self,
                 realm: Optional[str] = None,
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
        assert isinstance(reference, (type(None), Reference)), \
            f"MappableObject {self} initialized with invalid reference: {reference}"

        # If the reference is given, we need a realm in
        # which the reference is valid.
        assert reference is None or realm is not None, \
            f"reference provided but no realm in {type(self).__name__} " \
            f"construction."

        # We assume that objects that carry a reference have been
        # saved in the location given by the reference.
        super().__init__(
            realm
            if reference is not None and not reference.is_none_reference()
            else None
        )

        self.realm = realm
        self.reference = reference
        self.mapped = reference is None

    @property
    def modifiable_sub_objects(self) -> Iterable["MappableObject"]:
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
        return self.modifiable_sub_objects_impl()

    def read_in(self,
                backend_type: str = "git"
                ) -> "MappableObject":

        from dataladmetadatamodel.mapper import get_mapper

        if self.mapped is False:

            assert self.realm is not None
            assert self.reference is not None

            # If the reference is a None-reference,
            # we can handle this here.
            if self.reference.is_none_reference():
                assert self.reference.class_name == type(self).__name__
                logger.warning(f"read_in({self}): None-reference in {self}")
                self.purge_impl()
                return self

            # Ensure that the object is saved on the given realm
            if not self.is_saved_on(self.realm):
                logger.error(
                    f"read_in({self}): trying to overwrite a modified object")
                raise RuntimeError(
                    "read_in({self}): tried to read over a modified object")

            # The object is not mapped, but saved on self.realm,
            # use the mappable object-specific mapper to read
            # the object in.
            get_mapper(
                type(self).__name__,
                backend_type).map_in(
                    self,
                    self.realm,
                    self.reference)

            # Mark the object as mapped.
            self.mapped = True

        else:

            logger.debug(
                f"read_in({self}): not needed, object is already mapped")

        return self

    def write_out(self,
                  destination_realm: Optional[str] = None,
                  backend_type: str = "git",
                  force_write: bool = False) -> Reference:

        from dataladmetadatamodel.mapper import get_mapper

        # If the object is not mapped and not modified,
        # we do not have to do anything.
        if not self.mapped:

            assert isinstance(self.realm, str), \
                f"write_out: object {self} has no valid " \
                f"realm: {self.realm}"
            assert isinstance(self.reference, Reference), \
                f"write_out: object {self} has no valid " \
                f"reference: {self.reference}"

            if not self.is_saved_on(destination_realm):
                raise RuntimeError(
                    f"write_out({self}): modified object got lost "
                    f"on {destination_realm}")

            logger.debug(
                f"write_out({self}): not needed, object already"
                f" saved on {destination_realm}")
            return self.reference

        if self.realm:
            destination_realm = destination_realm or self.realm

        assert destination_realm is not None, \
            f"write_out({self}): no destination available for {self}"

        if Reference.is_remote(destination_realm):
            raise RuntimeError(
                f"write_out({self}): trying to write to a remote realm: "
                f"{destination_realm}")

        self.realm = destination_realm

        if self.is_saved_on(destination_realm):
            if not force_write:
                logger.debug(
                    f"write_out({self}): skipping map_out because {self} "
                    f"is already stored on {destination_realm}")
                return self.reference

            logger.debug(
                f"write_out({self}): forcing map_out, although {self} "
                f"is already stored on {destination_realm}")

        logger.debug(
            f"write_out({self}): calling map_out to save {self} "
            f"to {destination_realm}")

        self.reference = get_mapper(
            type(self).__name__,
            backend_type).map_out(
                self,
                destination_realm,
                force_write)

        self.set_saved_on(destination_realm)

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
            self.mapped = True
            return True
        return False

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_destination: Optional[str] = None,
                 **kwargs) -> "MappableObject":

        with ensure_mapped(self):
            result = self.deepcopy_impl(new_mapper_family,
                                        new_destination,
                                        **kwargs)
        return result

    @abstractmethod
    def modifiable_sub_objects_impl(self) -> Iterable["MappableObject"]:
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
