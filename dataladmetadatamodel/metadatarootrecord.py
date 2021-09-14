from uuid import UUID
from typing import Optional

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.mapper.reference import Reference


class MetadataRootRecord(MappableObject):
    def __init__(self,
                 dataset_identifier: UUID,
                 dataset_version: str,
                 dataset_level_metadata: "Metadata",
                 file_tree: "FileTree"):

        super().__init__()
        self.mapper_family = mapper_family
        self.realm = realm
        self.dataset_identifier = dataset_identifier
        self.dataset_version = dataset_version
        self.dataset_level_metadata = dataset_level_metadata
        self.file_tree = file_tree

    def save(self) -> Reference:
        """
        This method persists the bottom-half of all modified
        connectors by delegating it to the ConnectorDict. Then
        it saves the properties of the UUIDSet and the top-half
        of the connectors with the appropriate class mapper.
        """
        self.un_touch()
        return self.unmap_myself(self.mapper_family, self.realm)

    def set_file_tree(self, file_tree: FileTree):
        self.touch()
        self.file_tree = file_tree

    def get_file_tree(self):
        return self.file_tree.load_object()

    def set_dataset_level_metadata(self, dataset_level_metadata: Metadata):
        self.touch()
        self.dataset_level_metadata = dataset_level_metadata

    def get_dataset_level_metadata(self):
        return self.dataset_level_metadata.load_object()

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "MetadataRootRecord":

        new_mapper_family = new_mapper_family or self.mapper_family
        new_realm = new_realm or self.realm

        copied_metadata_root_record = MetadataRootRecord(
            new_mapper_family,
            new_realm,
            self.dataset_identifier,
            self.dataset_version,
            self.dataset_level_metadata.deepcopy(new_mapper_family, new_realm),
            self.file_tree.deepcopy(new_mapper_family, new_realm))

        return copied_metadata_root_record
