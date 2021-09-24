from typing import (
    Any,
    Iterable,
    Optional,
    Tuple
)

from dataladmetadatamodel.mappableobject import MappableObject
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
    """
    def __init__(self,
                 leaf_class: Any,
                 mtree: Optional[MTreeNode] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(mtree, (type(None), MTreeNode))
        assert isinstance(reference, (type(None), Reference))

        if mtree is None:
            self.mtree = MTreeNode(leaf_class=leaf_class,
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
                 **kwargs) -> "MTreeProxy":

        return type(self)(self.mtree.deepcopy(new_mapper_family,
                          new_destination,
                          **kwargs))

    def get_paths_recursive(self,
                            show_intermediate: Optional[bool] = False
                            ) -> Iterable[Tuple[MetadataPath, MappableObject]]:
        yield from self.mtree.get_paths_recursive(show_intermediate)
