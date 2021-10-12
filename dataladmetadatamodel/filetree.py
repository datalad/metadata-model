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
from dataladmetadatamodel.mtreeproxy import MTreeProxy
from dataladmetadatamodel.mapper.reference import Reference


class FileTree(MTreeProxy):
    def __init__(self,
                 mtree: Optional[MTreeNode] = None,
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(mtree, (type(None), MTreeNode))
        assert isinstance(reference, (type(None), Reference))

        super().__init__(Metadata, mtree, realm, reference)

    def add_metadata(self,
                     path: MetadataPath,
                     metadata: Metadata):

        self.mtree.add_child_at(metadata, path)

    def get_metadata(self,
                     path: MetadataPath
                     ) -> Optional[Metadata]:

        metadata = self.mtree.get_object_at_path(path)

        if metadata is None:
            return None

        assert isinstance(metadata, Metadata)
        metadata.ensure_mapped()
        return metadata

    def unget_metadata(self,
                       metadata: Metadata,
                       destination: Optional[str] = None):
        assert isinstance(metadata, Metadata)
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
