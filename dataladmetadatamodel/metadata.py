import json
import time
from typing import Dict, Generator, Iterable, List, Optional, Set, Tuple, Union

from .connector import ConnectedObject
from .mapper import get_mapper
from .mapper.reference import Reference


JSONObject = Union[List["JSONObject"], Dict[str, "JSONObject"], int, float, str]


class ParameterDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class ExtractorConfiguration:
    """
    Holds a single configuration for an extractor.
    Ensures that a version number is at least given.
    """
    def __init__(self,
                 version: str,
                 parameter: Dict[str, JSONObject]):
        self.version = version
        self.parameter = ParameterDict(parameter)

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

    def __eq__(self, other):
        return (
            self.version == other.version
            and self.parameter == other.parameter
        )

    def __hash__(self):
        return hash((self.version, self.parameter))

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


class MetadataInstanceSet:
    """
    A set of metadata instances, i.e. extractor
    run information records. Each instance is
    identified by its configuration, i.e. an
    instance of ExtractorConfiguration.
    """
    def __init__(self,
                 initial_metadata_instances: Optional[Iterable[MetadataInstance]]):

        self.parameter_set = list()
        self.instance_set = dict()
        for metadata_instance in initial_metadata_instances:
            self.add_metadata_instance(metadata_instance)

    def add_metadata_instance(self, metadata_instance: MetadataInstance):
        if metadata_instance.configuration not in self.parameter_set:
            self.parameter_set.append(metadata_instance.configuration)
        instance_key = self.parameter_set.index(metadata_instance)
        self.instance_set[instance_key] = metadata_instance

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="MetadataInstanceSet",
                version="1.0"
            ),
            "parameter_set": xxx,
            "instance_set": yyy
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_obj())

    @classmethod
    def from_json_obj(cls, obj: JSONObject) -> "MetadataInstanceSet":
        assert obj["@"]["type"] == "MetadataInstanceSet"
        assert obj["@"]["version"] == "1.0"
        return cls(
            obj["parameter_set"],
            obj["instance_set"]
        )

    @classmethod
    def from_json_str(cls, json_str: str) -> "MetadataInstanceSet":
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
                 initial_instances: Optional[Dict[int, Dict[ExtractorConfiguration, MetadataInstance]]] = None):

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

    def extractors(self) -> Generator[str, None, None]:
        yield from self.instances.keys()

    def extractor_runs(self) -> Generator[Tuple[str, Dict[ExtractorConfiguration, MetadataInstance]], None, None]:
        yield from self.instances.items()

    def add_extractor_run(self,
                          time_stamp: Optional[float],
                          extractor_name: str,
                          author_name: str,
                          author_email: str,
                          configuration: ExtractorConfiguration,
                          metadata_location: str):

        instance_dict = self.instances.get(extractor_name, dict())
        instance_dict[configuration] = MetadataInstance(
            time_stamp if time_stamp is not None else time.time(),
            author_name,
            author_email,
            configuration,
            metadata_location
        )
        self.instances[extractor_name] = instance_dict

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
