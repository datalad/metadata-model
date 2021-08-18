
from dataladmetadatamodel.mapper.gitmapper.objectreference import GitReference, add_tree_reference
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_str,
    git_ls_tree_recursive,
    git_save_str,
    git_save_tree)
from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.reference import Reference


empty_tree_location = "None"


class FileTreeGitMapper(BaseMapper):

    def _save_file_tree(self, node: "TreeNode") -> str:
        from dataladmetadatamodel.connector import Connector

        dir_entries = []
        for name, child_node in node.child_nodes.items():
            if child_node.is_leaf_node():
                assert isinstance(child_node.value, Connector)
                # Save connector, that will ensure that the reference is set.
                # TODO: move this save-call? Since this is a high level
                #  save-operation, it should probably be called in FileTree
                #  or TreeNode, but that would require another recursive
                #  descent.
                child_node.value.save_object()
                # Save connectors reference.
                location = git_save_str(
                    self.realm,
                    child_node.value.reference.to_json_str())
                dir_entries.append(("100644", "blob", location, name))
            else:
                dir_entries.append((
                    "040000",
                    "tree",
                    self._save_file_tree(child_node), name))

        if dir_entries:
            return git_save_tree(self.realm, dir_entries)
        else:
            return empty_tree_location

    def map(self, ref: Reference) -> "FileTree":
        from dataladmetadatamodel.connector import Connector
        from dataladmetadatamodel.filetree import FileTree
        from dataladmetadatamodel.metadatapath import MetadataPath
        from dataladmetadatamodel.treenode import TreeNode

        file_tree = FileTree("git", self.realm)
        if ref.location != empty_tree_location:
            for line in git_ls_tree_recursive(self.realm, ref.location):
                location, path = line[12:52], line[53:]
                connector = Connector.from_reference(
                    Reference.from_json_str(
                        git_load_str(self.realm, location)))
                file_tree.add_node_hierarchy(
                    MetadataPath(path),
                    TreeNode(connector))
        return file_tree

    def unmap(self, obj) -> str:
        """ Save FileTree as git file tree """
        from dataladmetadatamodel.filetree import FileTree

        assert isinstance(obj, FileTree)
        file_tree_hash = self._save_file_tree(obj)
        if file_tree_hash != empty_tree_location:
            add_tree_reference(GitReference.FILE_TREE, file_tree_hash)
        return file_tree_hash
