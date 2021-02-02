
from .gitbackend.subprocess import git_load_str, git_save_str
from ..basemapper import BaseMapper
from ..reference import Reference


class MetadataGitMapper(BaseMapper):

    def map(self, ref: Reference) -> "Metadata":
        from dataladmetadatamodel.metadata import Metadata
        return Metadata.from_json(
            git_load_str(self.realm, ref.location)
        )

    def unmap(self, obj) -> str:
        from dataladmetadatamodel.metadata import Metadata
        assert isinstance(obj, Metadata)
        return git_save_str(self.realm, obj.to_json())


