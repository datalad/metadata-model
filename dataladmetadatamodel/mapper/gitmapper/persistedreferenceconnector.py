from typing import Any

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
        persisted_ref_realm = self.reference.realm
        return ReferenceGitMapper(persisted_ref_realm).map(self.reference)

    def _save_metadata_reference(self, metadata_reference: Reference) -> str:
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

                location = self._save_metadata_reference(persisted_ref_reference)
                self.reference = Reference("git", persisted_ref_reference.realm, "Reference", location)

        else:
            if self.reference is None:
                self.reference = Reference.get_none_reference()

        return self.reference
