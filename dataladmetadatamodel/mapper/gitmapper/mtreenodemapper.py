
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_read_tree_node,
    git_save_tree_node,
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


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

        for entry in [line.split() for line in lines]:
            if entry[1] == "tree":
                child = MTreeNode(
                    leaf_class=mtree_node.leaf_class,
                    realm=realm,
                    reference=Reference("MTreeNode",
                                        entry[2]))

            elif entry[1] == "blob":
                child = mtree_node.leaf_class.get_empty_instance(
                    realm=realm,
                    reference=Reference(mtree_node.leaf_class_name,
                                        entry[2]))

            else:
                raise ValueError(f"unknown git tree entry type: {entry[1]}")
            mtree_node.child_nodes[entry[3]] = child

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
                child_name
            )
            for child_name, child_node in mtree_node.child_nodes.items()
        ]
        mtree_node_location = git_save_tree_node(realm, dir_entries)
        return Reference("MTreeNode", mtree_node_location)
