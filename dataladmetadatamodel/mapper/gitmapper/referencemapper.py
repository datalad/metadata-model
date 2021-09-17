from typing import Any

from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_str,
    git_save_str
)
from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.reference import Reference


class ReferenceGitMapper(BaseMapper):

    def map_impl(self, ref: Reference) -> Reference:
        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"
        if ref.is_none_reference():
            return Reference.get_none_reference("Reference")
        ref_json_str = git_load_str(self.realm, ref.location)
        return Reference.from_json_str(ref_json_str)

    def unmap_impl(self, ref: Any) -> Reference:
        assert isinstance(ref, Reference)
        return Reference(
            "git",
            self.realm,
            "Reference",
            git_save_str(self.realm, ref.to_json_str()))
