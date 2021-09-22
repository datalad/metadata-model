from typing import (
    Any,
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
                 leaf_class: Any,
                 reference: Optional[Reference] = None):
        super().__init__(reference)
        self.leaf_class = leaf_class
        self.leaf_class_name = leaf_class.__name__
        self.child_nodes = dict()

    def __contains__(self, path: MetadataPath) -> bool:
        return self.get_child(path) is not None

    def __str__(self):
        return f"<{type(self).__name__}: children: {self.child_nodes.keys()}>"

    def ensure_mapped(self) -> bool:
        if not self.mapped:
            self.read_in()
            return True
        return False

    def get_modifiable_sub_objects_impl(self) -> Iterable["MappableObject"]:
        yield from self.child_nodes.values()

    def purge_impl(self):
        for child_node in self.child_nodes.values():
            child_node.purge()
        self.child_nodes = dict()

    def new_node(self):
        return MTreeNode(self.leaf_class)

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "MappableObject":

        copied_mtree_node = self.new_node()
        for child_name, child_node in self.child_nodes.items():
            copied_mtree_node.add_child(
                child_name,
                child_node.deepcopy(
                    new_mapper_family,
                    new_destination))

        copied_mtree_node.write_out(new_destination)
        copied_mtree_node.purge()
        return copied_mtree_node

    def contains_child(self,
                       child_name: Union[str, MetadataPath]
                       ) -> bool:

        return self.get_child(child_name) is not None

    def get_child(self,
                  child_name: Union[str, MetadataPath]
                  ) -> Optional[MappableObject]:

        self.ensure_mapped()
        return self.child_nodes.get(str(child_name), None)

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

        self.ensure_mapped()
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
                     path: MetadataPath):

        assert len(path) > 0, "child name required"

        path_element = path.parts[0]
        existing_child = self.get_child(path_element)

        if len(path) == 1:
            if isinstance(existing_child, MTreeNode):
                raise ValueError(
                    f"tree-node named {path_element} exists: "
                    f"{existing_child}, cannot be converted "
                    f"to {child}")

            # Add the final object to self
            self.add_child(path.parts[0], child)

        else:

            if existing_child is None:
                # Create an intermediate node, if it doesn't exist
                existing_child = self.new_node()
                self.add_child(path_element, existing_child)

            if not isinstance(existing_child, MTreeNode):
                raise ValueError(
                    f"non tree-node named {path_element} exists: "
                    f"{existing_child}, cannot be converted to a "
                    f"tree-node")

            existing_child.add_child_at(
                child,
                MetadataPath(
                    "/".join(path.parts[1:])))

    def remove_child(self,
                     child_name: str):

        self.ensure_mapped()
        self.touch()
        del self.child_nodes[child_name]

    def remove_child_at(self,
                        path: MetadataPath):

        containing_path = MetadataPath("/".join(path.parts[:-1]))
        containing_node = self.get_object_at_path(containing_path)
        containing_node.remove_child(path.parts[-1])

    def get_object_at_path(self,
                           path: Optional[MetadataPath] = None
                           ) -> Optional["MTreeNode"]:

        # Linear search for path
        path = path or MetadataPath("")
        current_node = self
        for element in path.parts:
            if not isinstance(current_node, MTreeNode):
                return None
            current_node = current_node.get_child(element)
            if current_node is None:
                return None
        return current_node

    def get_paths_recursive(self,
                            show_intermediate: Optional[bool] = False
                            ) -> Iterable[Tuple[MetadataPath, "MappableObject"]]:

        if show_intermediate:
            yield MetadataPath(""), self

        purge_self = self.ensure_mapped()
        for child_name, child_node in self.child_nodes.items():
            if not isinstance(child_node, MTreeNode):
                yield MetadataPath(child_name), child_node
            else:
                for sub_path, tree_node in child_node.get_paths_recursive(
                        show_intermediate):
                    yield MetadataPath(child_name) / sub_path, tree_node

        if purge_self:
            #self.write_out()
            self.purge()

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
