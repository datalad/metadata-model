"""
Instances of the Text class just contain
text. Their main use is as dummy-element
during model development.
"""
from typing import (
    Iterable,
    Optional
)

from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.modifiableobject import ModifiableObject
from dataladmetadatamodel.mapper.reference import Reference


class Text(MappableObject):

    def __init__(self,
                 content: Optional[str] = None,
                 reference: Optional[Reference] = None):

        super().__init__(reference)
        self.content = content

    def get_modifiable_sub_objects_impl(self) -> Iterable[ModifiableObject]:
        return []

    def purge_impl(self, force: bool):
        self.content = None

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "Text":
        return Text(content=self.content, reference=self.reference)
