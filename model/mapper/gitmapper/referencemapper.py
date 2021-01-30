from typing import Any

from .gittools import git_load_str, git_save_str
from ..basemapper import BaseMapper
from ..reference import Reference


class ReferenceGitMapper(BaseMapper):

    def map(self, ref: Reference) -> Reference:
        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"
        ref_json_str = git_load_str(self.realm, ref.location)
        return Reference.from_json_str(ref_json_str)

    def unmap(self, ref: Any) -> str:
        assert isinstance(ref, Reference)
        return git_save_str(self.realm, ref.to_json_str())

