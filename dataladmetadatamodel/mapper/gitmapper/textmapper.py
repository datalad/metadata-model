
from .gittools import git_load_str, git_save_str
from ..basemapper import BaseMapper
from ..reference import Reference


class TextGitMapper(BaseMapper):

    def map(self, ref: Reference) -> "Text":
        from dataladmetadatamodel.text import Text
        content = git_load_str(self.realm, ref.location)
        return Text(content)

    def unmap(self, text) -> str:
        from dataladmetadatamodel.text import Text
        assert isinstance(text, Text)
        return git_save_str(self.realm, text.content)
