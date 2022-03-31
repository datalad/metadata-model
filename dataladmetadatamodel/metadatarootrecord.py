from uuid import UUID
from typing import (
    Iterable,
    Optional
)
from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.mapper.reference import Reference


class MetadataRootRecord(MappableObject):
    def __init__(self,
                 dataset_identifier: Optional[UUID],
                 dataset_version: Optional[str],
                 dataset_level_metadata: Optional[Metadata],
                 file_tree: Optional[FileTree],
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None
                 ):

        assert isinstance(dataset_identifier, (type(None), UUID))
        assert isinstance(dataset_version, (type(None), str))
        assert isinstance(dataset_level_metadata, (type(None), Metadata))
        assert isinstance(file_tree, (type(None), FileTree))
        assert isinstance(realm, (type(None), str))
        assert isinstance(reference, (type(None), Reference))

        super().__init__(realm, reference)
        self.dataset_identifier = dataset_identifier
        self.dataset_version = dataset_version
        self.dataset_level_metadata = dataset_level_metadata
        self._file_tree = file_tree

    @staticmethod
    def get_empty_instance(realm: Optional[str] = None,
                           reference: Optional[Reference] = None):
        return MetadataRootRecord(None, None, None, None, realm, reference)

    def modifiable_sub_objects_impl(self) -> Iterable[MappableObject]:
        return [
            child
            for child in [self.dataset_level_metadata, self._file_tree]
            if child is not None
        ]

    def purge_impl(self):
        self.dataset_level_metadata.purge()
        if self._file_tree is not None:
            self._file_tree.purge()
        if self.dataset_level_metadata is not None:
            self.dataset_level_metadata = None
        self._file_tree = None

    def set_file_tree(self, file_tree: FileTree):
        self.ensure_mapped()
        self.touch()
        self._file_tree = file_tree

    def get_file_tree(self):
        self.ensure_mapped()
        if self._file_tree is None:
            return None
        return self._file_tree.read_in()

    file_tree = property(fget=get_file_tree, fset=set_file_tree)

    def set_dataset_level_metadata(self, dataset_level_metadata: Metadata):
        self.ensure_mapped()
        self.touch()
        self.dataset_level_metadata = dataset_level_metadata

    def get_dataset_level_metadata(self):
        self.ensure_mapped()
        return self.dataset_level_metadata.read_in()

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "MetadataRootRecord":

        copied_metadata_root_record = MetadataRootRecord(
            self.dataset_identifier,
            self.dataset_version,
            (
                self.dataset_level_metadata.deepcopy(
                    new_mapper_family,
                    new_destination)
                if self.dataset_level_metadata is not None
                else None
            ),
            (
                self._file_tree.deepcopy(
                    new_mapper_family,
                    new_destination)
                if self._file_tree is not None
                else None
            ),
            None,
            None
        )

        copied_metadata_root_record.write_out(new_destination)
        copied_metadata_root_record.purge()

        return copied_metadata_root_record
