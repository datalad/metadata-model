
from dataladmetadatamodel.mapper.gitmapper.objectreference import (
    GitReference,
    add_blob_reference
)
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_str,
    git_save_str
)
from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.reference import Reference


class MetadataGitMapper(BaseMapper):

    def map_impl(self, ref: Reference) -> "Metadata":
        from dataladmetadatamodel.metadata import Metadata
        return Metadata.from_json(
            git_load_str(self.realm, ref.location)
        )

    def unmap_impl(self, obj) -> Reference:
        from dataladmetadatamodel.metadata import Metadata
        assert isinstance(obj, Metadata)

        metadata_object_hash = git_save_str(self.realm, obj.to_json())
        add_blob_reference(GitReference.METADATA, metadata_object_hash)
        return Reference("git", self.realm, "Metadata", metadata_object_hash)
