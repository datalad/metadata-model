import json
from typing import Optional

from dataladmetadatamodel import (
    check_serialized_version,
    version_string
)


none_class_name = "*None*"
none_location = "*None*"
none_mapper_family_name = "*None*"
none_realm = "*None*"


class Reference:
    def __init__(self,
                 mapper_family: str,
                 realm: str,
                 class_name: str,
                 location: Optional[str] = None):
        self.mapper_family = mapper_family
        self.realm = realm
        self.class_name = class_name
        self.location = location

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"Reference(mapper_family='{self.mapper_family}', "
            f"realm='{self.realm}', "
            f"class_name='{self.class_name}', "
            f"location={repr(self.location)})")

    def is_none_reference(self) -> bool:
        return self.location == none_location and self.class_name == none_class_name

    def to_json_str(self):
        return json.dumps(self.to_json_obj())

    def to_json_obj(self):
        return {
            "@": dict(
                type="Reference",
                version=version_string,
            ),
            **dict(
                mapper_family=self.mapper_family,
                realm=self.realm,
                class_name=self.class_name,
                location=self.location)
        }

    @classmethod
    def from_json_str(cls, json_str: str) -> "Reference":
        return cls.from_json_obj(json.loads(json_str))

    @classmethod
    def from_json_obj(cls, obj) -> "Reference":
        assert obj["@"]["type"] == "Reference"
        check_serialized_version(obj)
        return cls(
            obj["mapper_family"],
            obj["realm"],
            obj["class_name"],
            obj["location"]
        )

    @classmethod
    def get_none_reference(cls) -> "Reference":
        return cls(none_mapper_family_name, none_realm, none_class_name, none_location)
