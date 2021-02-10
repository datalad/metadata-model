import json
from typing import Optional


none_class_name = "*None*"
none_location = "*None*"


class Reference:
    def __init__(self,
                 mapper_family: str,
                 class_name: str,
                 location: Optional[str] = None):
        self.mapper_family = mapper_family
        self.class_name = class_name
        self.location = location

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"Reference(mapper_family='{self.mapper_family}', "
            f"class_name='{self.class_name}', "
            f"location={repr(self.location)})")

    def is_none_reference(self) -> bool:
        return self.location == none_location

    def to_json_str(self):
        return json.dumps(self.to_json_obj())

    def to_json_obj(self):
        return {
            "@": dict(
                type="Reference",
                version="1.0",
            ),
            **dict(
                mapper_family=self.mapper_family,
                class_name=self.class_name,
                location=self.location)
        }

    @classmethod
    def from_json_str(cls, json_str: str) -> "Reference":
        return cls.from_json_obj(json.loads(json_str))

    @classmethod
    def from_json_obj(cls, obj) -> "Reference":
        assert obj["@"]["type"] == "Reference"
        assert obj["@"]["version"] == "1.0"
        return cls(
            obj["mapper_family"],
            obj["class_name"],
            obj["location"]
        )

    @classmethod
    def get_none_reference(cls, mapper_family: str, class_name: str) -> "Reference":
        return cls(mapper_family, class_name, none_location)
