from typing import (
    cast,
    Any,
    Iterable,
    Optional,
    Tuple
)

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.mapper.gitmapper.metadatamapper import MetadataGitMapper
from dataladmetadatamodel.mapper.gitmapper.objectreference import (
    add_tree_reference,
    GitReference,
)
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.mtreenode import MTreeNode
from dataladmetadatamodel.mapper.reference import Reference


class MTreeProxy:
    """
    Base class for all classes that use MTreeNode internally,
    but are not themselves mappable. Those classes typically
    require a stored tree, but do not add additional
    "data-fields", but just convenience methods. Examples are
    "DatasetTree" and "FileTree". Still those classes are
    contained within other mappable objects and therefore should
    behave like a mappable object.
    This class proxies the common MappableObject-interface calls
    to the underlying MTreeNode object.
    # TODO: this could probably be a mixin.
    """
    def __init__(self,
                 leaf_class: Any,
                 mtree: Optional[MTreeNode] = None,
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(mtree, (type(None), MTreeNode))
        assert isinstance(reference, (type(None), Reference))

        if mtree is None:
            self.mtree = MTreeNode(leaf_class=leaf_class,
                                   realm=realm,
                                   reference=reference)
        else:
            assert mtree.leaf_class == leaf_class
            self.mtree = mtree

    def __contains__(self, path: MetadataPath) -> bool:
        return self.mtree.get_object_at_path(path) is not None

    def ensure_mapped(self) -> bool:
        return self.mtree.ensure_mapped()

    def read_in(self, backend_type="git") -> MappableObject:
        self.mtree.read_in(backend_type)
        return cast(MappableObject, self)

    def write_out(self,
                  destination: Optional[str] = None,
                  backend_type: str = "git",
                  force_write: bool = False) -> Reference:

        # Since a file tree might contain a large number
        # of metadata entries and since each entry requires
        # two blobs to be written, we use a write-cache.

        # TODO: ugly:
        from .filetree import FileTree

        cache_destination = destination or self.mtree.realm
        if isinstance(self, FileTree):
            MetadataGitMapper.cache_realm(cache_destination)

        reference = self.mtree.write_out(destination,
                                         backend_type,
                                         force_write)

        if isinstance(self, FileTree):
            MetadataGitMapper.flush_realm(cache_destination)

        if not reference.is_none_reference():
            add_tree_reference(reference.location)
        return reference

    def purge(self):
        return self.mtree.purge()

    def is_saved_on(self, destination: str):
        return self.mtree.is_saved_on(destination)

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_destination: Optional[str] = None,
                 **kwargs) -> "MTreeProxy":

        return type(self)(self.mtree.deepcopy(new_mapper_family,
                          new_destination,
                          **kwargs))

    def get_paths_recursive(self,
                            show_intermediate: Optional[bool] = False
                            ) -> Iterable[Tuple[MetadataPath, MappableObject]]:
        yield from self.mtree.get_paths_recursive(show_intermediate)
