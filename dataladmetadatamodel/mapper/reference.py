import json
import logging
from typing import Optional

from dataladmetadatamodel import (
    check_serialized_version,
    version_string
)


logger = logging.getLogger("datalad.metadatamodel.mapper")

none_class_name = "*None*"
none_location = "*None*"


class Reference:
    def __init__(self,
                 class_name: str,
                 location: Optional[str] = None):

        assert isinstance(location, str) or location is None, \
                f"location is not a string: {location}"

        self.class_name = class_name
        self.location = location

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"Reference(class_name='{self.class_name}', "
            f"location={repr(self.location)})")

    def __eq__(self, other):
        return (
            self.class_name == other.class_name
            and self.location == other.location
        )

    def assign_from(self, other: "Reference"):
        self.class_name = other.class_name
        self.location = other.location

    def is_none_reference(self) -> bool:
        return self.location == none_location

    def to_json_str(self):
        return json.dumps(self.to_json_obj())

    def to_json_obj(self):
        return {
            "@": dict(
                type="Reference",
                version=version_string),
            **dict(
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
        if "mapper_family" in obj or "realm" in obj:
            logger.info(f"old reference object found: {obj}")
        return cls(
            obj["class_name"],
            obj["location"]
        )

    @classmethod
    def get_none_reference(cls, referred_class_name: str) -> "Reference":
        return cls(referred_class_name, none_location)

    @staticmethod
    def is_remote(realm):
        return any(
            map(
                lambda pattern: realm.startswith(pattern),
                [
                   "git@",
                   "git:",
                   "http:",
                   "https:",
                   "ssh:"]))

    @staticmethod
    def is_local(realm):
        return not Reference.is_remote(realm)
