from typing import Any

from dataladmetadatamodel.mapper.gitmapper.gitbackend.subprocess import (
    git_load_json,
    git_save_json
)
from dataladmetadatamodel.mapper.mapper import Mapper
from dataladmetadatamodel.mapper.reference import Reference


class ReferenceGitMapper(Mapper):

    def map_in_impl(self,
                    reference_to_map_in: Reference,
                    reference: Reference) -> None:

        assert isinstance(reference_to_map_in, Reference)
        assert isinstance(reference, Reference)
        assert reference.mapper_family == "git"

        reference_to_map_in.assign_from(
            Reference.from_json_obj(
                git_load_json(
                    reference.realm,
                    reference.location)))

    def map_out_impl(self,
                     reference_to_map_out: Reference,
                     destination: str,
                     force_write: bool) -> Reference:

        assert isinstance(reference_to_map_out, Reference)
        return Reference(
            "git",
            destination,
            "Reference",
            git_save_json(destination, reference_to_map_out.to_json_obj()))
