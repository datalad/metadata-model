from uuid import UUID

from .connector import ConnectedObject, Connector
from .mapper import get_mapper
from .mapper.reference import Reference


class MetadataRootRecord(ConnectedObject):
    def __init__(self,
                 mapper_family,
                 realm,
                 dataset_identifier: UUID,
                 dataset_version: str,
                 dataset_level_metadata: Connector,
                 file_tree: Connector):

        self.mapper_family = mapper_family
        self.realm = realm
        self.dataset_identifier = dataset_identifier
        self.dataset_version = dataset_version
        self.dataset_level_metadata = dataset_level_metadata
        self.file_tree = file_tree

    def save(self, force_write: bool = False) -> Reference:
        """
        This method persists the bottom-half of all modified
        connectors by delegating it to the ConnectorDict. Then
        it saves the properties of the UUIDSet and the top-half
        of the connectors with the appropriate class mapper.
        """
        self.save_connected_components(force_write)
        return Reference(
            self.mapper_family,
            "MetadataRootRecord",
            get_mapper(
                self.mapper_family,
                "MetadataRootRecord")(self.realm).unmap(self))

    def save_connected_components(self, force_write: bool = False):
        self.file_tree.save_object(self.mapper_family, self.realm, force_write)
        self.dataset_level_metadata.save_object(self.mapper_family, self.realm, force_write)

    def set_file_tree(self, file_tree: ConnectedObject):
        self.file_tree = Connector.from_object(file_tree)

    def get_file_tree(self):
        return self.file_tree.load_object(self.mapper_family, self.realm)

    def set_dataset_level_metadata(self, dataset_level_metadata: ConnectedObject):
        self.dataset_level_metadata = Connector.from_object(dataset_level_metadata)

    def get_dataset_level_metadata(self):
        return self.dataset_level_metadata.load_object(self.mapper_family, self.realm)
