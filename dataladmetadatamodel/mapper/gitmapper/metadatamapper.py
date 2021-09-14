
from dataladmetadatamodel.mapper.gitmapper.objectreference import (
    GitReference,
    add_blob_reference
)
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_str,
    git_save_str
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class MetadataGitMapper(Mapper):

    def map_in_impl(self,
                    metadata: "Metadata",
                    reference: Reference) -> None:

        from dataladmetadatamodel.metadata import Metadata

        assert isinstance(metadata, Metadata)
        metadata.init_from_json(
            git_load_str(reference.realm, reference.location))

    def map_out_impl(self,
                     metadata: "Metadata",
                     destination: str,
                     force_write: bool) -> Reference:

        from dataladmetadatamodel.metadata import Metadata
        assert isinstance(metadata, Metadata)

        metadata_location = git_save_str(destination, metadata.to_json())
        add_blob_reference(GitReference.METADATA, metadata_location)
        return Reference("git", destination, "Metadata", metadata_location)
