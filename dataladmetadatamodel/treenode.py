from typing import (
    Any,
    Iterable,
    List,
    Optional,
    Tuple
)

from dataladmetadatamodel.metadatapath import MetadataPath


class TreeNode:
    def __init__(self,
                 value: Optional[Any] = None):
        self.child_nodes = dict()
        self.value = value

    def __contains__(self, path: MetadataPath) -> bool:
        assert isinstance(path, MetadataPath)
        return self.get_node_at_path(path) is not None

    def is_leaf_node(self):
        return len(self.child_nodes) == 0

    def _add_node(self, node_name: str, new_node: "TreeNode"):
        """
        Add a single sub-node with the given name.
        """
        self._add_nodes([(node_name, new_node)])

    def _add_nodes(self,
                   new_nodes: List[Tuple[str, "TreeNode"]]):

        # Assert that there is no name is a single ".", and that
        # no name contains a "/".
        assert all(map(lambda nn: nn[0] != ".", new_nodes))
        assert all(map(lambda nn: nn[0].find("/") < 0, new_nodes))

        # Assert that there are no duplicated names
        assert len(set(map(lambda nn: nn[0], new_nodes))) == len(new_nodes)

        new_names = set(map(lambda nn: nn[0], new_nodes))
        duplicated_names = set(self.child_nodes.keys()) & new_names

        if duplicated_names:
            raise ValueError(
                "Name(s) already exist(s): " + ", ".join(duplicated_names))

        self.child_nodes = {
            **self.child_nodes,
            **dict(new_nodes)
        }

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
            self._add_node(path_elements[0], new_node)
        else:
            sub_node = self.child_nodes.get(path_elements[0], None)
            if not sub_node:
                sub_node = TreeNode()
                self._add_node(path_elements[0], sub_node)
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

        """ Simple linear path-search """
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

    @staticmethod
    def is_root_path(path: MetadataPath) -> bool:
        return len(path.parts) == 0
