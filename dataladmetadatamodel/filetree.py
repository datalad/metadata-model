from typing import (
    Iterable,
    Optional,
    Tuple
)

from dataladmetadatamodel import JSONObject
from dataladmetadatamodel.metadata import (
    ExtractorConfiguration,
    Metadata
)
from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.mapper.reference import Reference


class FileTree:
    def __init__(self,
                 mtree: Optional[MTreeNode] = None,
                 reference: Optional[Reference] = None):

        if mtree is None:
            self.mtree = MTreeNode(leaf_class=Metadata,
                                   reference=reference)
        else:
            assert mtree.leaf_class == Metadata
            self.mtree = mtree

    def __contains__(self, path: MetadataPath) -> bool:
        return self.mtree.contains_child(path)

    def add_metadata(self,
                     path: MetadataPath,
                     metadata: Metadata):

        self.mtree.add_child_at(metadata, path)

    def get_metadata(self,
                     path: MetadataPath
                     ) -> Optional[Metadata]:

        return self.mtree.get_object_at_path(path)

    def unget_metadata(self,
                       path: MetadataPath,
                       destination: Optional[str] = None):
        metadata = self.get_metadata(path)
        metadata.write_out(destination)
        metadata.purge()

    def add_extractor_run(self,
                          path,
                          time_stamp: Optional[float],
                          extractor_name: str,
                          author_name: str,
                          author_email: str,
                          configuration: ExtractorConfiguration,
                          metadata_content: JSONObject):

        try:
            metadata = self.get_metadata(path)
        except AttributeError:
            metadata = Metadata()
            self.add_metadata(path, metadata)

        metadata.add_extractor_run(
            time_stamp,
            extractor_name,
            author_name,
            author_email,
            configuration,
            metadata_content
        )

    def get_paths_recursive(self,
                            show_intermediate: Optional[bool] = False
                            ) -> Iterable[Tuple[MetadataPath, MappableObject]]:
        yield from self.mtree.get_paths_recursive(show_intermediate)

    def read_in(self, backend_type="git") -> MappableObject:
        self.mtree.read_in(backend_type)
        return self

    def write_out(self,
                  destination: Optional[str] = None,
                  backend_type: str = "git",
                  force_write: bool = False) -> Reference:

        return self.mtree.write_out(destination,
                                    backend_type,
                                    force_write)

    def purge(self):
        return self.mtree.purge()

    def is_saved_on(self, destination: str):
        return self.mtree.is_saved_on(destination)

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_destination: Optional[str] = None,
                 **kwargs) -> "FileTree":

        return FileTree(self.mtree.deepcopy(new_mapper_family,
                                            new_destination,
                                            **kwargs))


x = """
class FileTree(MappableObject, TreeNode):
    def __init__(self,
                 reference: Optional[Reference] = None):

        MappableObject.__init__(self, reference)
        TreeNode.__init__(self)

    def __contains__(self, path: Union[str, MetadataPath]) -> bool:
        # Allow strings as input as well
        if isinstance(path, str):
            path = MetadataPath(path)
        node = self.get_node_at_path(path)
        # The check for node.value is not None takes care of root paths
        return node is not None and node.value is not None

    def get_modifiable_sub_objects_impl(self) -> Iterable[MappableObject]:
        for name, tree_node in super().get_paths_recursive():
            if tree_node.value is not None:
                yield tree_node.value

    def purge_impl(self):
        for name, tree_node in super().get_paths_recursive():
            if tree_node.value is not None:
                yield tree_node.value.purge(force)
        TreeNode.__init__(self)

    def add_directory(self, name):
        self.touch()
        self._add_node(name, TreeNode())

    def add_file(self, path):
        self.touch()
        self.add_node_hierarchy(path, TreeNode())

    def add_metadata(self,
                     path: MetadataPath,
                     metadata: Metadata):
        self.touch()
        self.add_node_hierarchy(path, TreeNode(value=metadata))

    def get_metadata(self, path: MetadataPath) -> Optional[Metadata]:
        value = self.get_node_at_path(path).value
        if value is not None:
            return value.read_in()
        return None

    def set_metadata(self, path: MetadataPath, metadata: Metadata):
        self.touch()
        self.get_node_at_path(path).value.set(metadata)

    def unget_metadata(self, path: MetadataPath, destination: str):
        value = self.get_node_at_path(path).value
        value.write_out(destination)
        value.purge()

    def get_paths_recursive(self,
                            show_intermediate: Optional[bool] = False
                            ) -> Iterable[Tuple[MetadataPath, Metadata]]:

        for name, tree_node in super().get_paths_recursive(show_intermediate):
            yield name, tree_node.value

    def add_extractor_run(self,
                          path,
                          time_stamp: Optional[float],
                          extractor_name: str,
                          author_name: str,
                          author_email: str,
                          configuration: ExtractorConfiguration,
                          metadata_content: JSONObject):

        self.touch()

        try:
            metadata = self.get_metadata(path)
        except AttributeError:
            metadata = Metadata()
            self.add_metadata(path, metadata)

        metadata.add_extractor_run(
            time_stamp,
            extractor_name,
            author_name,
            author_email,
            configuration,
            metadata_content
        )

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "FileTree":

        copied_file_tree = FileTree()

        for path, metadata in self.get_paths_recursive(True):
            if metadata is not None:
                copied_metadata = metadata.deepcopy(new_mapper_family, new_destination)
            else:
                copied_metadata = None
            copied_file_tree.add_node_hierarchy(
                path,
                TreeNode(value=copied_metadata),
                allow_leaf_node_conversion=True)

        copied_file_tree.write_out(new_destination)
        copied_file_tree.purge()

        return copied_file_tree
"""