from typing import (
    Dict,
    List,
    Optional
)

from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_save_tree
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class MTreeNodeGitMapper(Mapper):

    def map_in_impl(self,
                    mtree_node: "MTreeNode",
                    reference: Reference) -> None:

        from dataladmetadatamodel.metadata import Metadata
        from dataladmetadatamodel.mtreenode import MTreeNode

        if not reference.is_none_reference():

            git_tree_info = git_read_tree(reference.realm, reference.location)
            file_tree.mapper_private_data["git"] = git_tree_info

            for entry in git_tree_info.values():
                if entry.type == "blob":
                    file_tree.add_node_hierarchy(
                        MetadataPath(entry.path),
                        TreeNode(
                            Metadata(
                                Reference(
                                    "git",
                                    reference.realm,
                                    "Metadata",
                                    entry.hash))))

        return file_tree

    def map_out_impl(self,
                     mtree_node: "MTreeNode",
                     destination: str,
                     force_write: bool) -> Reference:

        """
        Persists this tree node.
        """
        from dataladmetadatamodel.mtreenode import MTreeNode

        assert isinstance(mtree_node, MTreeNode)

        if mtree_node.is_leaf_node():
            return mtree_node.value.write_out(destination)

        assert mtree_node.value is None
        for child_name, child_node in mtree_node.child_nodes.values():
            child_node.write_out(destination)

        dir_entries = [
            (
                "100644" if child_node.is_leaf_node() else "040000",
                "blob" if child_node.is_leaf_node() else "tree",
                child_name,
                child_node.reference.location
            )
            for child_name, child_node in mtree_node.child_nodes.items()
        ]
        mtree_node_location = git_save_tree(destination, dir_entries)
        return Reference("git", destination, "MTreeNode", mtree_node_location)
