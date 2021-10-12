from dataladmetadatamodel.mapper.gitmapper.objectreference import (
    GitReference,
    add_blob_reference,
)
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_str,
    git_save_str,
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class MetadataGitMapper(Mapper):

    def map_in_impl(self,
                    metadata: "Metadata",
                    realm: str,
                    meta_reference: Reference) -> None:

        from dataladmetadatamodel.metadata import Metadata
        from dataladmetadatamodel.mapper.reference import Reference

        assert isinstance(metadata, Metadata)

        reference = Reference.from_json_str(
            git_load_str(realm, meta_reference.location))

        metadata.init_from_json(
            git_load_str(realm, reference.location))

    def map_out_impl(self,
                     metadata: "Metadata",
                     realm: str,
                     force_write: bool) -> Reference:

        from dataladmetadatamodel.metadata import Metadata
        assert isinstance(metadata, Metadata)

        # Save metadata object and add it to the
        # blob-references. That is necessary because
        # metadata blobs are only referenced in
        # persisted Reference-objects, i.e. in
        # JSON-strings that are stored in the
        # repository.
        metadata_blob_location = git_save_str(realm, metadata.to_json())
        add_blob_reference(GitReference.BLOBS, metadata_blob_location)

        # save reference
        metadata_reference_blob_location = git_save_str(
            realm,
            Reference(
                "Metadata",
                metadata_blob_location).to_json_str())

        # Return reference to reference, also it specifies
        # the class Metadata, it points actually to a
        # persisted Reference object. But this is only known
        # internally in this mapper.
        return Reference(
            "Metadata",
            metadata_reference_blob_location)
