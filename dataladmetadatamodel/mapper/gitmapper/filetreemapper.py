from dataclasses import dataclass, field
from typing import (
    Dict,
    List,
    Optional
)

from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_ls_tree_recursive,
    git_save_str,
    git_save_tree
)
from dataladmetadatamodel.mapper.gitmapper.objectreference import (
    GitReference,
    add_tree_reference
)
from dataladmetadatamodel.mapper.reference import Reference


empty_tree_location = "None"


# This is a simple internal representation of a git-tree
# to improve performance, it could become a real tree-based
# structure
@dataclass
class GitTreeEntry:
    flag: str
    type: str
    hash: str
    path: str
    dirty: bool = False
    parts: tuple = field(init=False)

    def __post_init__(self):
        self.parts = tuple(self.path.split("/"))


def get_children_at(git_tree_info: Dict[str, GitTreeEntry],
                    path: str) -> List[GitTreeEntry]:
    if path == "":
        node_parts = ()
    else:
        node_parts = tuple(path.split("/"))
    selected_entries = [
        entry
        for entry in git_tree_info.values()
        if len(entry.parts) == len(node_parts) + 1 and entry.parts[:-1] == node_parts
    ]
    return selected_entries


def get_node_at(git_tree_info: Dict[str, GitTreeEntry], path: str) -> Optional[GitTreeEntry]:
    return git_tree_info.get(path, None)


def get_intermediate_paths(path: str) -> List[str]:
    path_elements = path.split("/")
    return [
        "/".join(path_elements[0:i])
        for i in range(1, len(path_elements))]


def add_nodes_for_path(git_tree_info: Dict[str, GitTreeEntry],
                       flag: str,
                       node_type: str,
                       path: str):
    """ Add all tree nodes, if they do not yet exist """

    # Create nodes for intermediate paths
    for intermediate_path in get_intermediate_paths(path):
        if intermediate_path not in git_tree_info:
            git_tree_info[intermediate_path] = GitTreeEntry(
                "040000",
                "tree",
                "-",
                intermediate_path)

    # Create final element
    if path not in git_tree_info:
        git_tree_info[path] = GitTreeEntry(flag, node_type, "-", path)


def git_read_tree(realm: str, location: str) -> Dict[str, GitTreeEntry]:
    return {
        "": GitTreeEntry("000000", "root", location, ""),
        **{
            line.split()[3]: GitTreeEntry(*line.split())
            for line in git_ls_tree_recursive(realm, location, show_intermediate=True)
        }
    }


class FileTreeGitMapper(BaseMapper):

    def _save_new_file_tree(self,
                            node: "TreeNode"
                            ) -> Optional[str]:
        from dataladmetadatamodel.connector import Connector
        from dataladmetadatamodel.mapper.gitmapper.persistedreferenceconnector import PersistedReferenceConnector

        dir_entries = []
        for name, child_node in node.child_nodes.items():

            if child_node.is_leaf_node():
                metadata_connector = child_node.value
                assert isinstance(child_node.value, PersistedReferenceConnector)
                reference = metadata_connector.save_object()
                dir_entries.append(("100644", "blob", reference.location, name))

            else:
                sub_dir_hash = self._save_new_file_tree(child_node)
                if sub_dir_hash:
                    dir_entries.append(("040000", "tree", sub_dir_hash, name))

        if dir_entries:
            return git_save_tree(self.realm, dir_entries)
        else:
            return None

    def _save_existing_file_tree(self,
                                 node: "TreeNode",
                                 path: str,
                                 git_tree_info: Dict[str, GitTreeEntry]
                                 ) -> [bool, str]:

        from dataladmetadatamodel.mapper.gitmapper.persistedreferenceconnector import PersistedReferenceConnector

        # TODO: check for deleted entries
        level_changed = False

        for name, child_node in node.child_nodes.items():

            child_node_path = path + ("/" if path else "") + name

            # Add potential new nodes
            if child_node.is_leaf_node():
                add_nodes_for_path(git_tree_info, "100644", "blob", child_node_path)
            else:
                add_nodes_for_path(git_tree_info, "040000", "tree", child_node_path)

            entry = get_node_at(git_tree_info, child_node_path)

            if child_node.is_leaf_node():

                file_tree_connector = child_node.value
                assert isinstance(file_tree_connector, PersistedReferenceConnector)
                reference = file_tree_connector.save_object()

                # Check whether the entry was created or the hash has changed
                if entry.hash != reference.location:
                    entry.hash = reference.location
                    level_changed = True

            else:

                sub_tree_changed, child_tree_hash = self._save_existing_file_tree(child_node, child_node_path, git_tree_info)
                if sub_tree_changed and child_tree_hash != entry.hash:
                    entry.hash = child_tree_hash
                    level_changed = True

        if level_changed:
            dir_entries = [
                (entry.flag, entry.type, entry.hash, entry.path.split("/")[-1])
                for entry in get_children_at(git_tree_info, path)
                if entry.type != "root"
            ]
            return True, git_save_tree(self.realm, set(dir_entries))
        else:
            return False, git_tree_info[path].hash

    def map_impl(self, ref: Reference) -> "FileTree":
        from dataladmetadatamodel.filetree import FileTree
        from dataladmetadatamodel.metadatapath import MetadataPath
        from dataladmetadatamodel.treenode import TreeNode
        from dataladmetadatamodel.mapper.gitmapper.persistedreferenceconnector import PersistedReferenceConnector

        file_tree = FileTree("git", self.realm)
        if ref.location != empty_tree_location:

            git_tree_info = git_read_tree(self.realm, ref.location)
            file_tree.mapper_private_data["git"] = git_tree_info

            for entry in git_tree_info.values():
                if entry.type == "blob":
                    file_tree_connector = PersistedReferenceConnector(
                        Reference("git", self.realm, "None", entry.hash),
                        None,
                        False)
                    file_tree.add_node_hierarchy(
                        MetadataPath(entry.path),
                        TreeNode(file_tree_connector))

        return file_tree

    def unmap_impl(self, obj) -> Reference:
        """ Save FileTree as git file tree """
        from dataladmetadatamodel.filetree import FileTree

        assert isinstance(obj, FileTree)
        git_tree_info = obj.mapper_private_data.get("git", None)

        if git_tree_info is None:
            file_tree_hash = self._save_new_file_tree(obj)
        else:
            _, file_tree_hash = self._save_existing_file_tree(obj, "", git_tree_info)

        if file_tree_hash is None:
            return Reference.get_none_reference()

        add_tree_reference(GitReference.FILE_TREE, file_tree_hash)
        return Reference("git", self.realm, "FileTree", file_tree_hash)

    @staticmethod
    def get_connector_class():
        from dataladmetadatamodel.mapper.gitmapper.persistedreferenceconnector import PersistedReferenceConnector
        return PersistedReferenceConnector
