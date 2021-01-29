import enum

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

    def add_dataset(self, path, metadata_root_record: MetadataRootRecord):
        dataset_node = self.get_node_at_path(path)
        if dataset_node is None:
            self.add_node_hierarchy(path, TreeNode(metadata_root_record))
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
        file_node_set = self.get_paths_recursive(False)
        for _, _, file_node in file_node_set:
            file_node.value.save(force_write)

        return Reference(
            self.mapper_family,
            "DatasetTree",
            get_mapper(self.mapper_family, "DatasetTree")(self.realm).unmap(self))
