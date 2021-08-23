from typing import Iterable, Optional, Tuple, Union

from dataladmetadatamodel.connector import ConnectedObject
from dataladmetadatamodel.log import logger
from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.metadata import ExtractorConfiguration, Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.treenode import TreeNode
from dataladmetadatamodel.mapper.reference import Reference


class FileTree(ConnectedObject, TreeNode):
    def __init__(self,
                 mapper_family: str,
                 realm: str):

        ConnectedObject.__init__(self)
        TreeNode.__init__(self)
        self.mapper_family = mapper_family
        self.realm = realm
        self.mapper = get_mapper(mapper_family, "FileTree")
        self.connector_class = self.mapper.get_connector_class()

    def __contains__(self, path: Union[str, MetadataPath]) -> bool:
        # Allow strings as input as well
        if isinstance(path, str):
            path = MetadataPath(path)
        node = self.get_node_at_path(path)
        # The check for node.value is not None takes care of root paths
        return node is not None and node.value is not None

    def add_directory(self, name):
        self.touch()
        self._add_node(name, TreeNode())

    def add_file(self, path):
        self.touch()
        self.add_node_hierarchy(path, TreeNode())

    def add_metadata(self,
                     path: MetadataPath,
                     metadata: Optional[Metadata] = None):
        self.touch()
        self.add_node_hierarchy(
            path,
            TreeNode(value=self.connector_class(None, metadata, True)))

    def get_metadata(self, path: MetadataPath) -> Optional[Metadata]:
        return self.get_node_at_path(path).value.load_object()

    def set_metadata(self, path: MetadataPath, metadata: Metadata):
        self.touch()
        self.get_node_at_path(path).value.set(metadata)

    def unget_metadata(self, path: MetadataPath):
        value = self.get_node_at_path(path).value
        value.save_object()
        value.purge()

    def save(self) -> Reference:
        """
        Persists all file node values, i.e. all mapped metadata,
        if they are mapped or modified, then save the tree itself,
        with the class mapper.
        """
        self.un_touch()

        for path, metadata_connector in self.get_paths_recursive(False):
            # The following lines should not be required because the
            # mapper should have created a
            #if metadata_connector is None:
            #    metadata_connector = self.connector_class.from_reference(
            #        Reference.get_none_reference())
            if metadata_connector is not None:
                metadata_connector.save_object()
            else:
                logger.debug(f"Path {path} has None metadata connector associated")


        return Reference(
            self.mapper_family,
            self.realm,
            "FileTree",
            get_mapper(
                self.mapper_family,
                "FileTree")(self.realm).unmap(self))

    def get_paths_recursive(self,
                            show_intermediate: Optional[bool] = False
                            ) -> Iterable[Tuple[MetadataPath, "Connector"]]:

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
                          metadata_content: ConnectedObject):

        self.touch()

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
            metadata_content
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
                TreeNode(
                    value=copied_connector),
                allow_leaf_node_conversion=True)

        return copied_file_tree
