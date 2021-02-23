
from .gitbackend.subprocess import git_load_str, git_save_str
from ..basemapper import BaseMapper
from ..reference import Reference


class TextGitMapper(BaseMapper):

    def map(self, ref: Reference) -> "Text":
        from ...text import Text

        assert isinstance(ref, Reference)
        assert ref.mapper_family == "git"

        content = git_load_str(ref.realm, ref.location)
        return Text(ref.mapper_family, ref.realm, content)

    def unmap(self, text) -> str:
        from ...text import Text

        assert isinstance(text, Text)
        return git_save_str(self.realm, text.content)
