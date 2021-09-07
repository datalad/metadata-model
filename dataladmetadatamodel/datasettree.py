import enum
from typing import (
    List,
    Optional,
    Tuple
)

from dataladmetadatamodel.connector import ConnectedObject
from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.treenode import TreeNode
from dataladmetadatamodel.mapper.reference import Reference


class NodeType(enum.Enum):
    DIRECTORY = enum.auto()
    DATASET = enum.auto()
    INTERNAL = enum.auto()


class DatasetTree(ConnectedObject, TreeNode):
    def __init__(self,
                 mapper_family: str,
                 realm: str):

        ConnectedObject.__init__(self)
        TreeNode.__init__(self)
        self.mapper_family = mapper_family
        self.realm = realm

    def __contains__(self, path: MetadataPath) -> bool:
        # The check for node.value <> None takes care of root paths
        node = self.get_node_at_path(path)
        return node is not None and node.value is not None

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
        self.touch()
        self._add_node(name, TreeNode())

    def add_dataset(self,
                    path: MetadataPath,
                    metadata_root_record: MetadataRootRecord):

        self.touch()

        dataset_node = self.get_node_at_path(path)
        if dataset_node is None:
            self.add_node_hierarchy(
                path,
                TreeNode(metadata_root_record),
                allow_leaf_node_conversion=True)
        else:
            dataset_node.value = metadata_root_record

    def add_subtree(self,
                    subtree: "DatasetTree",
                    subtree_path: MetadataPath):

        assert subtree.mapper_family == self.mapper_family
        assert subtree.realm == self.realm

        self.touch()

        sub_node = TreeNode(subtree.value)
        for path, node in subtree.child_nodes.items():
            sub_node._add_node(path, node)

        self.add_node_hierarchy(
            subtree_path,
            sub_node,
            allow_leaf_node_conversion=True)

    def delete_subtree(self,
                       subtree_path: MetadataPath):
        if subtree_path == "":
            raise ValueError("cannot delete root tree node")
        all_nodes_in_path = self.get_all_nodes_in_path(subtree_path)
        if all_nodes_in_path is None:
            raise ValueError(f"no subtree at path {subtree_path}")

        self.touch()

        _, containing_node = all_nodes_in_path[-2]
        name_to_delete, _ = all_nodes_in_path[-1]
        del containing_node.child_nodes[name_to_delete]

    def get_metadata_root_record(self, path: MetadataPath):
        return self.get_node_at_path(path).value

    def save(self) -> Reference:
        """
        Persists the dataset tree. First save connected
        components in all metadata root records, if they
        are mapped or modified. Then persist the dataset-tree
        itself, with the class mapper.
        """
        self.un_touch()

        for _, file_node in self.get_paths_recursive(False):
            file_node.value.save()

        return Reference(
            self.mapper_family,
            self.realm,
            "DatasetTree",
            get_mapper(
                self.mapper_family,
                "DatasetTree")(self.realm).unmap(self))

    def get_dataset_paths(self) -> List[
                                       Tuple[
                                           MetadataPath,
                                           MetadataRootRecord
                                       ]]:
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
