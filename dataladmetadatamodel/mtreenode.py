from typing import (
    Iterable,
    List,
    Optional,
    Tuple,
    Union
)

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.mapper.reference import Reference


class MTreeNode(MappableObject):
    def __init__(self,
                 reference: Optional[Reference] = None):
        super().__init__(reference)
        self.child_nodes = dict()

    def __contains__(self, path: MetadataPath) -> bool:
        return self.get_child(path) is not None

    def __str__(self):
        return f"<{type(self).__name__}: children: {self.child_nodes.keys()}>"

    def get_modifiable_sub_objects_impl(self) -> Iterable["MappableObject"]:
        yield from self.child_nodes.values()

    def purge_impl(self):
        for child_node in self.child_nodes:
            child_node.purge()
        self.child_nodes = dict()

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "MappableObject":

        copied_mtree_node = MTreeNode()
        for child_name, child_node in self.child_nodes.items():
            copied_mtree_node._add_child(
                child_name,
                child_node.deepcopy(
                    new_mapper_family,
                    new_destination))

        copied_mtree_node.write_out()
        copied_mtree_node.purge()
        return copied_mtree_node

    def contains_child(self, child_name: Union[str, MetadataPath]) -> bool:
        return self.get_child(child_name) is not None

    def get_child(self,
                  child_name: Union[str, MetadataPath]
                  ) -> Optional[MappableObject]:
        if isinstance(child_name, MetadataPath):
            child_name = str(child_name.parts[0])
        return self.child_nodes.get(child_name, None)


    def add_child(self, node_name: str, child: MappableObject):
        """
        Add a sub-element with the given name. The sub-element
        can be an MTreeNode or any other MappableObject (usually
        it will be an MTreeNode, Metadata, or MetadataRootRecord.
        """
        self._add_children([(node_name, child)])

    def _add_children(self,
                      children: List[Tuple[str, MappableObject]]):

        # Assert that no name is "." or contains a "/", and
        # assert that there are no duplicated names in the input
        assert all(map(lambda nn: nn[0] != ".", children))
        assert all(map(lambda nn: nn[0].find("/") < 0, children))
        assert len(set(map(lambda nn: nn[0], children))) == len(children)

        new_names = set(map(lambda nn: nn[0], children))
        duplicated_names = set(self.child_nodes.keys()) & new_names
        if duplicated_names:
            raise ValueError(
                "Child node with the following name(s) already exist(s): "
                + ", ".join(duplicated_names))

        self.touch()
        self.child_nodes = {
            **self.child_nodes,
            **dict(children)
        }

    def add_child_at(self,
                     child: MappableObject,
                     path: MetadataPath,
                     anchor: "MTreeNode"):

        assert len(path) > 0, "name required"

        path_element = path.parts[0]
        existing_child = anchor.get_child(path_element)
        if len(path) == 1:
            if isinstance(existing_child, MTreeNode):
                raise ValueError(f"cannot convert {existing_child} to {child}")
            anchor.add_child(path.parts[0], child)
        else:
            if existing_child is not None:
                if not isinstance(existing_child, MTreeNode):
                    raise ValueError(f"path does not exist ({existing_child} is not an MTreeNode")
            else:
                existing_child = MTreeNode()
                anchor.add_child(path_element, existing_child)
            self.add_child_at(child, MatadataPath(path.parts[1:]), existing_child)

    x = """
    def add_node_hierarchy(self,
                           path: MetadataPath,
                           new_node: "TreeNode",
                           allow_leaf_node_conversion: bool = False):

        if self.is_root_path(path):
            self.value = new_node.value
            return

        self._add_node_hierarchy(
            path.parts,
            new_node,
            allow_leaf_node_conversion)

    def _add_node_hierarchy(self,
                            path_elements: Tuple[str],
                            new_node: "TreeNode",
                            allow_leaf_node_conversion: bool):

        if len(path_elements) == 1:
            self._add_child(path_elements[0], new_node)
        else:
            sub_node = self.child_nodes.get(path_elements[0], None)
            if not sub_node:
                sub_node = TreeNode()
                self._add_child(path_elements[0], sub_node)
            else:
                if not allow_leaf_node_conversion and sub_node.is_leaf_node():
                    raise ValueError(
                        f"Cannot replace leaf node with name "
                        f"{path_elements[0]} with a directory node")

            sub_node._add_node_hierarchy(
                path_elements[1:],
                new_node,
                allow_leaf_node_conversion)

    def add_node_hierarchies(self,
                             new_node_hierarchies: List[
                                 Tuple[
                                     MetadataPath,
                                     "TreeNode"]]):

        for path_node_tuple in new_node_hierarchies:
            self.add_node_hierarchy(*path_node_tuple)

    def get_sub_node(self, name: str):
        return self.child_nodes[name]

    def get_node_at_path(self,
                         path: Optional[MetadataPath] = None
                         ) -> Optional["TreeNode"]:

        # Simple linear path-search
        path = path or MetadataPath("")
        current_node = self
        for element in path.parts:
            try:
                current_node = current_node.get_sub_node(element)
            except KeyError:
                return None
        return current_node

    def get_all_nodes_in_path(self,
                              path: Optional[MetadataPath] = None
                              ) -> Optional[List[Tuple[str, "TreeNode"]]]:

        path = path or MetadataPath("")
        result = [("", self)]
        current_node = self
        for element in path.parts:
            try:
                current_node = current_node.get_sub_node(element)
                result.append((element, current_node))
            except KeyError:
                return None
        return result

    def get_paths_recursive(self,
                            show_intermediate: Optional[bool] = False
                            ) -> Iterable[Tuple[MetadataPath, "TreeNode"]]:

        if show_intermediate or self.is_leaf_node():
            yield MetadataPath(""), self

        for child_name, child_node in self.child_nodes.items():
            for sub_path, tree_node in child_node.get_paths_recursive(
                    show_intermediate):
                yield MetadataPath(child_name) / sub_path, tree_node

    """

    @staticmethod
    def is_root_path(path: MetadataPath) -> bool:
        return len(path.parts) == 0
