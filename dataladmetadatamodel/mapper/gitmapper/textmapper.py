
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_str,
    git_save_str
)
from dataladmetadatamodel.mapper.basemapper import BaseMapper
from dataladmetadatamodel.mapper.reference import Reference


class TextGitMapper(BaseMapper):

    def map_impl(self, ref: Reference) -> "Text":
        from ...text import Text

        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"

        content = git_load_str(ref.realm, ref.location)
        return Text(ref.mapper_family, ref.realm, content)

    def unmap_impl(self, text) -> Reference:
        from ...text import Text

        assert isinstance(text, Text)
        text_location = git_save_str(self.realm, text.content)
        return Reference("git", self.realm, "Text", text_location)
