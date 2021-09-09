"""
Instances of the Text class just contain
text. Their main use is as dummy-element
during model development.
"""
from typing import Optional

from dataladmetadatamodel.connector import ConnectedObject
from dataladmetadatamodel.mapper import get_mapper
from dataladmetadatamodel.mapper.reference import Reference


class Text(ConnectedObject):

    def __init__(self,
                 mapper_family: str,
                 realm: str,
                 content: str):

        super().__init__()
        self.mapper_family = mapper_family
        self.realm = realm
        self.content = content

    def save(self) -> Reference:
        self.un_touch()
        return self.unmap_myself(self.mapper_family, self.realm)

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None
                 ) -> "Text":

        return Text(new_mapper_family, new_realm, self.content)
