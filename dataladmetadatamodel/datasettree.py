import enum
from typing import List, Optional, Tuple

from .connector import ConnectedObject
from .mapper import get_mapper
from .metadatarootrecord import MetadataRootRecord
from .treenode import TreeNode
from .mapper.reference import Reference


class NodeType(enum.Enum):
    DIRECTORY = enum.auto()
    DATASET = enum.auto()
    INTERNAL = enum.auto()


class DatasetTree(ConnectedObject, TreeNode):
    def __init__(self,
                 mapper_family: str,
                 realm: str):

        super(DatasetTree, self).__init__()
        self.mapper_family = mapper_family
        self.realm = realm

    def node_type(self):
        if self.is_leaf_node():
            assert self.value is not None
            return NodeType.DATASET
        else:
            if self.value is None:
                return NodeType.DIRECTORY
            else:
                return NodeType.DATASET

    def add_directory(self, name):
        self.add_node(name, TreeNode())

    def add_dataset(self,
                    path: str,
                    metadata_root_record: MetadataRootRecord):

        dataset_node = self.get_node_at_path(path)
        if dataset_node is None:
            self.add_node_hierarchy(
                path,
                TreeNode(metadata_root_record),
                allow_leaf_node_conversion=True)
        else:
            dataset_node.value = metadata_root_record

    def get_metadata_root_record(self, path: str):
        return self.get_node_at_path(path).value

    def save(self, force_write: bool = False) -> Reference:
        """
        Persists the dataset tree. First save connected
        components in all metadata root records, if they
        are mapped or modified. Then persist the dataset-tree
        itself, with the class mapper.
        """
        for _, file_node in self.get_paths_recursive(False):
            file_node.value.save(force_write)

        return Reference(
            self.mapper_family,
            self.realm,
            "DatasetTree",
            get_mapper(
                self.mapper_family,
                "DatasetTree")(self.realm).unmap(self))

    def get_dataset_paths(self) -> List[Tuple[str, MetadataRootRecord]]:
        return [
            (name, node.value)
            for name, node in self.get_paths_recursive(True)
            if node.value is not None
        ]

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None) -> "DatasetTree":

        copied_dataset_tree = DatasetTree(
            new_mapper_family or self.mapper_family,
            new_realm or self.realm)

        for path, node in self.get_paths_recursive(True):
            if node.value is not None:
                assert isinstance(node.value, MetadataRootRecord)
                copied_value = node.value.deepcopy(new_mapper_family, new_realm)
                copied_dataset_tree.add_dataset(path, copied_value)

        return copied_dataset_tree
