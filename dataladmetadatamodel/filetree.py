from typing import Generator, Optional, Tuple

from . import JSONObject
from .connector import ConnectedObject, Connector
from .mapper import get_mapper
from .metadata import ExtractorConfiguration, Metadata
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

    def get_metadata(self, path: str) -> Optional[Metadata]:
        return self.get_node_at_path(path).value.load_object()

    def set_metadata(self, path: str, metadata: Metadata):
        self.get_node_at_path(path).value.set(metadata)

    def unget_metadata(self, path: str, force_write: bool = False):
        value = self.get_node_at_path(path).value
        value.save_object(self.mapper_family, self.realm, force_write)
        value.purge()

    def save(self, force_write: bool = False) -> Reference:
        """
        Persists all file node values, i.e. all mapped metadata,
        if they are mapped or modified Then save the tree itself,
        with the class mapper.
        """
        for _, metadata_connector in self.get_paths_recursive(False):
            if metadata_connector is None:
                metadata_connector = Connector.from_reference(
                    Reference.get_none_reference(self.mapper_family, self.realm))
            metadata_connector.save_object(self.mapper_family, self.realm, force_write)
        return Reference(
            self.mapper_family,
            self.realm,
            "FileTree",
            get_mapper(
                self.mapper_family,
                "FileTree")(self.realm).unmap(self))

    def get_paths_recursive(self,
                            show_intermediate: Optional[bool] = False
                            ) -> Generator[Tuple[str, Connector], None, None]:

        for name, tree_node in super().get_paths_recursive(show_intermediate):
            yield name, tree_node.value

    def add_extractor_run(self,
                          mapper_family,
                          realm,
                          path,
                          time_stamp: Optional[float],
                          extractor_name: str,
                          author_name: str,
                          author_email: str,
                          configuration: ExtractorConfiguration,
                          metadata_location: JSONObject):

        try:
            metadata = self.get_metadata(path)
        except AttributeError:
            metadata = Metadata(mapper_family, realm)
            self.add_metadata(path, metadata)

        metadata.add_extractor_run(
            time_stamp,
            extractor_name,
            author_name,
            author_email,
            configuration,
            metadata_location
        )

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None) -> "FileTree":

        copied_file_tree = FileTree(
            new_mapper_family or self.mapper_family,
            new_realm or self.realm)

        for path, connector in self.get_paths_recursive(True):
            if connector is not None:
                copied_connector = connector.deepcopy(
                    new_mapper_family,
                    new_realm)
            else:
                copied_connector = None

            copied_file_tree.add_node_hierarchy(
                path,
                TreeNode(value=copied_connector),
                allow_leaf_node_conversion=True)

        return copied_file_tree
