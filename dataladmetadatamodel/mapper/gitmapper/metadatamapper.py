
from dataladmetadatamodel.mapper.gitmapper.objectreference import GitReference, add_blob_reference
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import git_load_str, git_save_str
from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.reference import Reference


class MetadataGitMapper(BaseMapper):

    def map(self, ref: Reference) -> "Metadata":
        from dataladmetadatamodel.metadata import Metadata
        return Metadata.from_json(
            git_load_str(self.realm, ref.location)
        )

    def unmap(self, obj) -> str:
        from dataladmetadatamodel.metadata import Metadata
        assert isinstance(obj, Metadata)

        metadata_object_hash = git_save_str(self.realm, obj.to_json())
        add_blob_reference(GitReference.METADATA, metadata_object_hash)
        return metadata_object_hash
