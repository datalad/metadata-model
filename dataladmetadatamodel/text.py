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
from dataladmetadatamodel.mapper.reference import Reference


class Text(MappableObject):

    def __init__(self,
                 content: Optional[str] = None,
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(content, (type(None), str))
        assert isinstance(reference, (type(None), Reference))

        super().__init__(realm, reference)
        self.content = content

    @staticmethod
    def get_empty_instance(realm: Optional[str] = None,
                           reference: Optional[Reference] = None):
        return Text(None, realm, reference)

    def get_modifiable_sub_objects_impl(self) -> Iterable[MappableObject]:
        return []

    def purge_impl(self):
        self.content = None

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "Text":

        copied_text = Text()
        copied_text.write_out(new_destination)
        return copied_text
