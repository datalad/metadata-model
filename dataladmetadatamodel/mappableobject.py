from typing import Optional


from dataladmetadatamodel.modifiableobject import ModifiableObject
from dataladmetadatamodel.mapper.xxx import get_mapper
from dataladmetadatamodel.mapper.reference import Reference


class MappableObject(ModifiableObject):
    """
    Base class for objects that can
    be mapped onto a storage backend
    """
    def __init__(self, reference: Optional[Reference]):
        super().__init__()
        self.reference = reference
        if reference is None:
            self.mapped = True
        else:
            self.mapped = False

    def read_in(self, backend_type="git"):
        if self.mapped:
            return
        assert self.reference is not None
        get_mapper(type(self).__name__, backend_type).read_in(self, self.reference)
        self.mapped = True
        self.clean()

    def write_out(self, destination: str, backend_type: str = "git") -> Reference:
        if self.mapped:
            self.reference = get_mapper(type(self).__name__, backend_type).write_out(self, destination)
            self.clean()
        assert self.reference is not None
        return self.reference

    def purge(self):
        if self.mapped:
            self.purge_impl()
            self.mapped = False
            self.clean()

    def purge_impl(self):
        raise NotImplementedError
