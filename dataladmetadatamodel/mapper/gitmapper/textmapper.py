
from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_str,
    git_save_str
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class TextGitMapper(Mapper):

    def map_in_impl(self,
                    text: "Text",
                    reference: Reference) -> None:

        from ...text import Text

        assert isinstance(text, Text)
        assert isinstance(reference, Reference)

        assert reference.mapper_family == "git"
        assert reference.class_name == "Text"

        text.content = git_load_str(reference.realm, reference.location)
        # TODO: what about the references?

    def map_out_impl(self,
                     text: "Text",
                     destination: str,
                     force_write: bool) -> Reference:

        from ...text import Text

        assert isinstance(text, Text)

        text_location = git_save_str(destination, text.content)
        return Reference("git", destination, "Text", text_location)
