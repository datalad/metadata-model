from copy import copy
from uuid import UUID
from typing import (
    Iterable,
    Optional
)
from dataladmetadatamodel.modifiableobject import ModifiableObject
from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.mapper.reference import Reference


class MetadataRootRecord(MappableObject):
    def __init__(self,
                 dataset_identifier: UUID,
                 dataset_version: str,
                 dataset_level_metadata: "Metadata",
                 file_tree: "FileTree",
                 reference: Optional[Reference] = None,
                 backend_type: str = "git"):

        super().__init__(reference)
        self.dataset_identifier = dataset_identifier
        self.dataset_version = dataset_version
        self.dataset_level_metadata = dataset_level_metadata
        self.file_tree = file_tree
        self.backend_type = backend_type

    def get_modifiable_sub_objects(self) -> Iterable[ModifiableObject]:
        return [self.dataset_level_metadata, self.file_tree]

    def purge_impl(self, force: bool):
        self.dataset_level_metadata.purge(force)
        self.file_tree.purge(force)
        self.dataset_level_metadata = None
        self.file_tree = None

    def set_file_tree(self, file_tree: FileTree):
        self.touch()
        self.file_tree = file_tree

    def get_file_tree(self):
        return self.file_tree.read_in(self.backend_type)

    def set_dataset_level_metadata(self, dataset_level_metadata: Metadata):
        self.touch()
        self.dataset_level_metadata = dataset_level_metadata

    def get_dataset_level_metadata(self):
        return self.dataset_level_metadata.read_in(self.backend_type)

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None) -> "MetadataRootRecord":

        copied_metadata_root_record = MetadataRootRecord(
            self.dataset_identifier,
            self.dataset_version,
            self.dataset_level_metadata.deepcopy(new_mapper_family,new_destination),
            self.file_tree.deepcopy(new_mapper_family, new_destination),
            None,
            self.backend_type)

        copied_metadata_root_record.write_out(new_destination)
        copied_metadata_root_record.purge()

        return copied_metadata_root_record
