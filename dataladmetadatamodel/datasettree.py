import enum
from typing import (
    Iterable,
    List,
    Optional,
    Tuple
)

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.modifiableobject import ModifiableObject
from dataladmetadatamodel.treenode import TreeNode
from dataladmetadatamodel.mapper.reference import Reference


class NodeType(enum.Enum):
    DIRECTORY = enum.auto()
    DATASET = enum.auto()
    INTERNAL = enum.auto()


class DatasetTree(MappableObject, TreeNode):
    def __init__(self,
                 reference: Optional[Reference] = None):

        MappableObject.__init__(self, reference)
        TreeNode.__init__(self)

    def __contains__(self, path: MetadataPath) -> bool:
        # The check for node.value <> None takes care of root paths
        node = self.get_node_at_path(path)
        return node is not None and node.value is not None

    def purge_impl(self, force: bool):
        for sub_object in self.get_modifiable_sub_objects():
            sub_object.purge(force)
        # Remove dataset tree
        TreeNode.__init__(self)

    def get_modifiable_sub_objects_impl(self) -> Iterable[ModifiableObject]:
        for _, tree_node in self.get_paths_recursive():
            if tree_node.value is not None:
                yield tree_node.value

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

    def get_metadata_root_record(self, path: MetadataPath) -> MetadataRootRecord:
        return self.get_node_at_path(path).value

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

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "DatasetTree":

        copied_dataset_tree = DatasetTree()
        for path, node in self.get_paths_recursive(True):
            if node.value is not None:
                assert isinstance(node.value, MetadataRootRecord)
                copied_value = node.value.deepcopy(new_mapper_family, new_destination)
                copied_dataset_tree.add_dataset(path, copied_value)

        copied_dataset_tree.write_out(new_destination)
        copied_dataset_tree.purge()
        return copied_dataset_tree
