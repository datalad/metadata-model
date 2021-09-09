"""
A PersistentReferenceConnector is a Connector
that connects to a final object via a persisted
reference, i.e. a Reference that is stored in git

persisted_reference_connector -> Reference on disk -> final object

Instead of directly using the location as the
final object location, it assumes that the location
is a pointer to a reference, loads the reference
and from the reference's location the final object.

This allows to refer to "References" in tree-entries
of type blob, without having to load the reference
from disk.

Thus only references that are really loaded lead to
additional git repository reading. This is especially
useful for file-trees. Without this file-tree reading
would consist of reading the git-tree objects and all
persisted references
"""


from typing import (
    Any,
    Optional
)

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.log import logger
from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.mapper.reference import Reference
from dataladmetadatamodel.mapper.gitmapper.referencemapper import ReferenceGitMapper


class PersistedReferenceConnector(Connector):
    """
    A connector that connects git blob-references, found in
    git-trees, which point to persisted references with the
    referenced object
    """
    def _load_metadata_reference(self) -> Reference:
        return ReferenceGitMapper(self.reference.realm).map(self.reference)

    def _save_metadata_reference(self, metadata_reference: Reference) -> Reference:
        return ReferenceGitMapper(metadata_reference.realm).unmap(metadata_reference)

    def load_object(self) -> Any:
        """
        If the object is not loaded, fetch the persisted reference and
        map the object pointed to by the persisted reference.
        """
        if not self.is_mapped:
            assert self.reference is not None
            if self.reference.is_none_reference():
                self.object = None
            else:

                metadata_reference = self._load_metadata_reference()
                logger.debug(f"PersistedReferenceConnector.load_object: mapping {metadata_reference} (pointed to by: {self.reference})")
                self.object = get_mapper(
                    "git",
                    metadata_reference.class_name)(self.reference.realm).map(metadata_reference)
                self.object.post_load(
                    self.reference.mapper_family,
                    self.reference.realm)
                self.object.un_touch()

            self.is_mapped = True
        return self.object

    def save_object(self) -> Reference:
        """
        Save the connected object, if it is modified and save the
        state of the connector itself.

        Saving the connected object is delegated to the object via
        ConnectedObject.save().
        """
        if self.is_mapped:
            if self.object is None:
                self.reference = Reference.get_none_reference()
            else:

                # TODO: performance improvement by checking for modification
                #  of the object

                logger.debug(f"PersistedReferenceConnector.save_object: saving {type(self.object)}")
                persisted_ref_reference = self.object.save()

                self.reference = self._save_metadata_reference(persisted_ref_reference)

        else:
            if self.reference is None:
                self.reference = Reference.get_none_reference()

        return self.reference

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "PersistedReferenceConnector":
        """
        Create a copy of the persisted reference connector.
        The copied connector will be connected to a copy of
        the original persisted reference, which will be connected
        to a copy of the original object.
        The connected object will be copied in the following steps:

          1. Loading the persisted reference
          2. Loading the original object
          3. Calling deepcopy on the original object to get a copied object
          4. Purging the original object
          5. Creating a persisted reference for the new object
          6. Storing the persisted reference
          7. Creating a persisted reference connector from the copied object
        """

        assert new_mapper_family == "git", "PersistedReferenceConnector can only be copied to git-mapped backend"

        logger.debug(f"{type(self)}.deepcopy: copying {type(self.object)}")

        if self.is_mapped:
            original_object = self.object
            purge_original = False
        else:
            original_object = self.load_object()
            purge_original = True

        copied_object = original_object.deepcopy(
            new_mapper_family,
            new_realm)

        if purge_original:
            self.purge()

        reference_to_copy = copied_object.save()
        rtc_reference = self._save_metadata_reference(reference_to_copy)

        copied_connector = PersistedReferenceConnector(
            rtc_reference,
            copied_object,
            True)

        # Create a connector instance with the same class as self
        copied_connector.save_object()
        copied_connector.purge()

        return copied_connector
