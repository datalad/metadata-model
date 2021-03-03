from uuid import UUID
from typing import Optional

from .connector import ConnectedObject, Connector
from .mapper import get_mapper
from .mapper.reference import Reference


class MetadataRootRecord(ConnectedObject):
    def __init__(self,
                 mapper_family: str,
                 realm: str,
                 dataset_identifier: UUID,
                 dataset_version: str,
                 dataset_level_metadata: Connector,
                 file_tree: Connector):

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

        self.file_tree.save_object()
        self.dataset_level_metadata.save_object()

        return Reference(
            self.mapper_family,
            self.realm,
            "MetadataRootRecord",
            get_mapper(
                self.mapper_family,
                "MetadataRootRecord")(self.realm).unmap(self))

    def set_file_tree(self, file_tree: ConnectedObject):
        self.touch()
        self.file_tree = Connector.from_object(file_tree)

    def get_file_tree(self):
        return self.file_tree.load_object()

    def set_dataset_level_metadata(self, dataset_level_metadata: ConnectedObject):
        self.touch()
        self.dataset_level_metadata = Connector.from_object(dataset_level_metadata)

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
