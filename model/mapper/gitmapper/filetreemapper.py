

from .gittools import git_load_str, git_ls_tree_recursive, git_save_str, git_save_tree
from ..basemapper import BaseMapper
from ..reference import Reference


class FileTreeGitMapper(BaseMapper):

    def _save(self, node: "TreeNode") -> str:
        from model.connector import Connector
        dir_entries = []
        for name, child_node in node.child_nodes.items():
            if child_node.is_leaf_node():
                assert isinstance(child_node.value, Connector)
                # Save connectors reference.
                location = git_save_str(self.realm, child_node.value.reference.to_json())
                dir_entries.append(("100644", "blob", location, name))
            else:
                dir_entries.append(("040000", "tree", self._save(child_node), name))
        return git_save_tree(self.realm, dir_entries)

    def map(self, ref: Reference) -> "FileTree":
        from model.connector import Connector
        from model.filetree import FileTree
        from model.treenode import TreeNode
        file_tree = FileTree("git", self.realm)
        for line in git_ls_tree_recursive(self.realm, ref.location):
            _, _, location, path = line.split()
            connector = Connector.from_reference(
                Reference.from_json(
                    git_load_str(self.realm, location)))
            file_tree.add_node_hierarchy(path, TreeNode(connector))
        return file_tree

    def unmap(self, obj) -> str:
        """ Save FileTree as git file tree """
        from model.filetree import FileTree
        assert isinstance(obj, FileTree)
        return self._save(obj)
