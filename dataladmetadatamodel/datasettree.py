from typing import (
    cast,
    List,
    Optional,
    Tuple,
)

from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.mtreeproxy import MTreeProxy
from dataladmetadatamodel.mapper.reference import Reference


datalad_root_record_name = ".datalad_metadata_root_record"


class DatasetTree(MTreeProxy):
    def __init__(self,
                 mtree: Optional[MTreeNode] = None,
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(mtree, (type(None), MTreeNode))
        assert isinstance(realm, (type(None), str))
        assert isinstance(reference, (type(None), Reference))

        super().__init__(MetadataRootRecord, mtree, realm, reference)

    def __contains__(self, path: MetadataPath) -> bool:
        return self.mtree.get_object_at_path(path / datalad_root_record_name) is not None

    def add_dataset(self,
                    path: MetadataPath,
                    metadata_root_record: MetadataRootRecord):

        self.mtree.add_child_at(metadata_root_record,
                                path / datalad_root_record_name)

    def get_metadata_root_record(self,
                                 path: MetadataPath
                                 ) -> Optional[MetadataRootRecord]:

        mrr = self.mtree.get_object_at_path(
            path / datalad_root_record_name)

        if mrr is None:
            return None

        assert isinstance(mrr, MetadataRootRecord)
        mrr.ensure_mapped()
        return mrr

    @property
    def dataset_paths(self
                      ) -> List[Tuple[MetadataPath, MetadataRootRecord]]:
        return [
            (
                MetadataPath("/".join(path.parts[:-1])),
                cast(MetadataRootRecord, node)
            )
            for path, node in self.mtree.get_paths_recursive()
            if path.parts[-1] == datalad_root_record_name
        ]

    def add_subtree(self,
                    subtree: "DatasetTree",
                    subtree_path: MetadataPath):

        self.mtree.add_child_at(subtree.mtree, subtree_path)

    def delete_subtree(self,
                       subtree_path: MetadataPath):
        self.mtree.remove_child_at(subtree_path)
