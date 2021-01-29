import json
import time
from typing import Dict, List, Optional, Set, Union

from .connector import ConnectedObject
from .mapper import get_mapper
from .mapper.reference import Reference


JSONObject = Union[List["JSONObject"], Dict[str, "JSONObject"], int, float, str]


class ExtractorConfiguration:
    """
    Holds a single configuration for an extractor.
    Ensures that a version number is at least given.
    """
    def __init__(self,
                 version: str,
                 parameter: Dict[str, JSONObject]):
        self.version = version
        self.parameter = parameter

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="ExtractorConfiguration",
                version="1.0"
            ),
            "version": self.version,
            "parameter": self.parameter
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_obj())

    @classmethod
    def from_json_obj(cls, obj: JSONObject) -> "ExtractorConfiguration":
        assert obj["@"]["type"] == "ExtractorConfiguration"
        assert obj["@"]["version"] == "1.0"
        return cls(
            obj["version"],
            obj["parameter"]
        )

    @classmethod
    def from_json_str(cls, json_str: str) -> "ExtractorConfiguration":
        return cls.from_json_obj(json.loads(json_str))


class MetadataInstance:
    """
    A single metadata instance. It is associated
    with provenance information, i.e. time stamp,
    author, author_email, with a configuration, i.e.
    parameters, and with a source that points to
    the metadata itself.
    """
    def __init__(self,
                 time_stamp,
                 author_name,
                 author_email,
                 configuration: ExtractorConfiguration,
                 metadata_location: str):

        self.time_stamp = time_stamp
        self.author_name = author_name
        self.author_email = author_email
        self.configuration = configuration
        self.metadata_location = metadata_location

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="MetadataInstance",
                version="1.0"
            ),
            "time_stamp": self.time_stamp,
            "author": self.author_name,
            "author_email": self.author_email,
            "configuration": self.configuration.to_json_obj(),
            "metadata_location": self.metadata_location
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_obj())

    @classmethod
    def from_json_obj(cls, obj: JSONObject) -> "MetadataInstance":
        assert obj["@"]["type"] == "MetadataInstance"
        assert obj["@"]["version"] == "1.0"
        return cls(
            obj["time_stamp"],
            obj["author"],
            obj["author_email"],
            ExtractorConfiguration.from_json_obj(obj["configuration"]),
            obj["metadata_location"]
        )

    @classmethod
    def from_json_str(cls, json_str: str) -> "MetadataInstance":
        return cls.from_json_obj(json.loads(json_str))


class Metadata(ConnectedObject):
    """
    Holds entries for all metadata of a single object.
    Metadata is identified on the first level by its
    format-name, i.e. the extractor-name. For each
    extractor there is a set of configurations and
    associated metadata, i.e. objects that contain
    the extractor result, aka the real metadata.
    """
    def __init__(self,
                 mapper_family: str,
                 realm: str,
                 initial_instances: Optional[Dict[str, Set[MetadataInstance]]] = None):

        self.mapper_family = mapper_family
        self.realm = realm
        self.instances = initial_instances or dict()

    def to_json(self) -> str:
        return json.dumps({
            "@": dict(
                type="Metadata",
                version="1.0"
            ),
            "mapper_family": self.mapper_family,
            "realm": self.realm,
            "instances": {
                format_name: [
                    instance.to_json_obj()
                    for instance in instance_set
                ]
                for format_name, instance_set in self.instances.items()
            }
        })

    def save(self) -> Reference:
        return Reference(
            self.mapper_family,
            "Metadata",
            get_mapper(self.mapper_family, "Metadata")(self.realm).unmap(self))

    def get_extractor_names(self):
        return self.instances.keys()

    def get_extractor_runs(self, extractor_name: str) -> Set[MetadataInstance]:
        return self.instances[extractor_name]

    def add_extractor_run(self,
                          time_stamp: Optional[int],
                          extractor_name: str,
                          author_name: str,
                          author_email: str,
                          configuration: ExtractorConfiguration,
                          metadata_location: str):

        instance_set = self.instances.get(extractor_name, set())
        instance_set.add(
            MetadataInstance(
                (
                    time_stamp
                    if time_stamp is not None
                    else int(time.time())
                ),
                author_name,
                author_email,
                configuration,
                metadata_location
            )
        )
        self.instances[extractor_name] = instance_set

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str)
        assert obj["@"]["type"] == "Metadata"
        assert obj["@"]["version"] == "1.0"
        instances = {
            format_name: set([
                MetadataInstance.from_json_obj(instance_json)
                for instance_json in instance_list_json
            ])
            for format_name, instance_list_json in obj["instances"].items()
        }
        return cls(
            obj["mapper_family"],
            obj["realm"],
            instances
        )
