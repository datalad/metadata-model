from typing import Optional

from .connector import ConnectedObject, Connector
from .mapper import get_mapper
from .metadata import Metadata
from .treenode import TreeNode
from .mapper.reference import Reference


class FileTree(ConnectedObject, TreeNode):
    def __init__(self,
                 mapper_family: str,
                 realm: str):

        super(FileTree, self).__init__()
        self.mapper_family = mapper_family
        self.realm = realm

    def add_directory(self, name):
        self.add_node(name, TreeNode())

    def add_file(self, path):
        self.add_node_hierarchy(path, TreeNode())

    def add_metadata(self, path: str, metadata: Optional[Metadata] = None):
        self.add_node_hierarchy(path, TreeNode(value=Connector.from_object(metadata)))

    def get_metadata(self, path: str):
        return self.get_node_at_path(path).value.load(self.mapper_family, self.realm)

    def set_metadata(self, path: str, metadata: Metadata):
        self.get_node_at_path(path).value.set(metadata)

    def unget_metadata(self, path: str, force_write: bool = False):
        value = self.get_node_at_path(path).value
        value.unmap(self.mapper_family, self.realm, force_write)
        value.purge()

    def save(self, force_write: bool = False) -> Reference:
        """
        Persists all file node values, i.e. all mapped metadata,
        if they are mapped or modified Then save the tree itself,
        with the class mapper.
        """
        file_node_set = self.get_paths_recursive(False)
        for _, file_node in file_node_set:
            file_node.value.save_object(self.mapper_family, self.realm, force_write)
        return Reference(
            self.mapper_family,
            "FileTree",
            get_mapper(self.mapper_family, "FileTree")(self.realm).unmap(self))
