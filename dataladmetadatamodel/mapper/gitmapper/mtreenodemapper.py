import codecs

from .gitbackend.subprocess import (
    git_read_tree_node,
    git_save_tree_node,
)
from .utils import split_git_lstree_line
from ..mapper import Mapper
from ..reference import Reference


class MTreeNodeGitMapper(Mapper):

    def map_in_impl(self,
                    mtree_node: "MTreeNode",
                    realm: str,
                    reference: Reference) -> None:

        from dataladmetadatamodel.mtreenode import MTreeNode

        if reference.is_none_reference():
            mtree_node.child_nodes = dict()
            return

        assert isinstance(mtree_node, MTreeNode)

        lines = git_read_tree_node(realm,
                                   reference.location)

        for line in lines:
            flag, node_type, hash_value, name = split_git_lstree_line(line)
            if name.startswith('"'):
                name = codecs.escape_decode(name[1:-1])[0].decode("utf-8")

            if node_type == "tree":
                child = MTreeNode(
                    leaf_class=mtree_node.leaf_class,
                    realm=realm,
                    reference=Reference("MTreeNode", hash_value))

            elif node_type == "blob":
                child = mtree_node.leaf_class.get_empty_instance(
                    realm=realm,
                    reference=Reference(mtree_node.leaf_class_name, hash_value))

            else:
                raise ValueError(f"unknown git tree entry type: {node_type}")
            mtree_node.child_nodes[name] = child

    def map_out_impl(self,
                     mtree_node: "MTreeNode",
                     realm: str,
                     force_write: bool) -> Reference:

        from dataladmetadatamodel.mtreenode import MTreeNode

        assert isinstance(mtree_node, MTreeNode)

        if not mtree_node.child_nodes:
            return Reference.get_none_reference("MTreeNode")

        for child_node in mtree_node.child_nodes.values():
            child_node.write_out(realm)

        dir_entries = [
            (
                "040000" if isinstance(child_node, MTreeNode) else "100644",
                "tree" if isinstance(child_node, MTreeNode) else "blob",
                child_node.reference.location,
                self.escape_double_quotes(child_name)
            )
            for child_name, child_node in mtree_node.child_nodes.items()
        ]
        mtree_node_location = git_save_tree_node(realm, dir_entries)
        return Reference("MTreeNode", mtree_node_location)

    @classmethod
    def escape_double_quotes(cls, input_string: str) -> str:
        if '"' in input_string:
            return (
                '"'
                + input_string
                .replace('\\', '\\\\')
                .replace('\"', '\\"')
                + '"'
            )
        else:
            return input_string
