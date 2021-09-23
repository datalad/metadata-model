from typing import (
    List,
    Optional,
    Tuple
)

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.mapper.reference import Reference


datalad_root_record_name = ".datalad_metadata_root_record"


class DatasetTree:
    def __init__(self,
                 mtree: Optional[MTreeNode] = None,
                 reference: Optional[Reference] = None):

        if mtree is None:
            self.mtree = MTreeNode(leaf_class=MetadataRootRecord,
                                   reference=reference)
        else:
            assert mtree.leaf_class == MetadataRootRecord
            self.mtree = mtree

    def __contains__(self, path: MetadataPath) -> bool:
        return self.mtree.contains_child(path)

    def add_dataset(self,
                    path: MetadataPath,
                    metadata_root_record: MetadataRootRecord):

        self.mtree.add_child_at(metadata_root_record,
                                path / datalad_root_record_name)

    def get_metadata_root_record(self,
                                 path: MetadataPath
                                 ) -> Optional[MetadataRootRecord]:

        mrr = self.mtree.get_object_at_path(path
                                            / datalad_root_record_name)
        if mrr is None:
            return None
        assert isinstance(mrr, MetadataRootRecord)
        return mrr

    def get_dataset_paths(self
                          ) -> List[Tuple[MetadataPath, MetadataRootRecord]]:
        return [
            (MetadataPath("/".join(path.parts[:-1])), node)
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

    def read_in(self, backend_type="git") -> MappableObject:
        self.mtree.read_in(backend_type)
        return self

    def write_out(self,
                  destination: Optional[str] = None,
                  backend_type: str = "git",
                  force_write: bool = False) -> Reference:

        return self.mtree.write_out(destination,
                                    backend_type,
                                    force_write)

    def purge(self):
        return self.mtree.purge()

    def is_saved_on(self, destination: str):
        return self.mtree.is_saved_on(destination)

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_destination: Optional[str] = None,
                 **kwargs) -> "DatasetTree":

        return DatasetTree(self.mtree.deepcopy(new_mapper_family,
                                               new_destination,
                                               **kwargs))


x = """
class DatasetTree(MappableObject, TreeNode):
    def __init__(self,
                 reference: Optional[Reference] = None):

        MappableObject.__init__(self, reference)
        TreeNode.__init__(self)

    def __contains__(self, path: MetadataPath) -> bool:
        # The check for node.value <> None takes care of root paths
        node = self.get_node_at_path(path)
        return node is not None and node.value is not None

    def purge_impl(self):
        for sub_object in self.get_modifiable_sub_objects():
            sub_object.purge()
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
"""