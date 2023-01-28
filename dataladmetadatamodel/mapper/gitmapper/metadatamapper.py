from typing import Dict

from dataladmetadatamodel.mapper.gitmapper.objectreference import add_blob_reference
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_str,
    git_save_str,
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference

from .gitblobcache import GitBlobCache


class MetadataGitMapper(Mapper):

    metadata_caches: Dict[str, GitBlobCache] = dict()

    @classmethod
    def get_cache(cls, realm: str):
        return cls.metadata_caches.get(realm, None)

    @classmethod
    def cache_realm(cls, realm: str):
        if cls.get_cache(realm) is not None:
            raise RuntimeError(f"already caching realm: {realm}")
        cls.metadata_caches[realm] = GitBlobCache(realm)

    @classmethod
    def flush_realm(cls, realm: str):
        cache = cls.get_cache(realm)
        if cache is None:
            raise RuntimeError(f"realm is not cached: {realm}")
        cache.flush()
        del cls.metadata_caches[realm]

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

        cache = self.get_cache(realm)
        if cache is None:
            return self.map_out_impl_immediate(metadata, realm, force_write)
        else:
            return self.map_out_impl_cached(cache, metadata, realm)

    def map_out_impl_immediate(self,
                               metadata: "Metadata",
                               realm: str,
                               force_write: bool) -> Reference:

        # Save metadata object and add it to the
        # blob-references. That is necessary because
        # metadata blobs are only referenced in
        # persisted Reference-objects, i.e. in
        # JSON-strings that are stored in the
        # repository.
        metadata_blob_location = git_save_str(realm, metadata.to_json())
        add_blob_reference(metadata_blob_location)

        # Save reference. NB we don't add the metadata reference to the object
        # tree here. Our "owner" will do that if necessary. For example, the
        # "MetadataRootRecord"-mapper will save the reference if it is used for
        # dataset-level metadata. It will not save it, if it is used for
        # file-level metadata, because that is reachable in a git-tree that is
        # added to the object tree.
        metadata_reference_blob_location = git_save_str(
            realm,
            Reference(
                "Metadata",
                metadata_blob_location).to_json_str())

        # Return reference to reference, although it specifies
        # the class Metadata, it points actually to a
        # persisted Reference object. But this is only known
        # internally in this mapper.
        return Reference(
            "Metadata",
            metadata_reference_blob_location)

    def map_out_impl_cached(self,
                            cache: GitBlobCache,
                            metadata: "Metadata",
                            realm: str) -> Reference:

        # Cache metadata, and cache a reference object. the
        # following code is "cache"-equivalent to the immediate case
        metadata_blob_location = cache.cache_blob(realm, metadata.to_json())
        add_blob_reference(metadata_blob_location)

        metadata_reference_blob_location = cache.cache_blob(
            realm,
            Reference(
                "Metadata",
                metadata_blob_location).to_json_str())

        return Reference(
            "Metadata",
            metadata_reference_blob_location)
