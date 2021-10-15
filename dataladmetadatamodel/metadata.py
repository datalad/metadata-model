import copy
import json
import time
from typing import (
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Tuple
)

from dataladmetadatamodel import (
    JSONObject,
    check_serialized_version,
    version_string
)
from dataladmetadatamodel.mappableobject import MappableObject
from dataladmetadatamodel.mapper.reference import Reference


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
                version=version_string
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
        check_serialized_version(obj)
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
                 metadata_content: JSONObject):

        self.time_stamp = time_stamp
        self.author_name = author_name
        self.author_email = author_email
        self.configuration = configuration
        self.metadata_content = metadata_content

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="MetadataInstance",
                version=version_string
            ),
            "time_stamp": self.time_stamp,
            "author": self.author_name,
            "author_email": self.author_email,
            "configuration": self.configuration.to_json_obj(),
            "metadata_content": self.metadata_content
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_obj())

    def __eq__(self, other):
        return (
                self.time_stamp == other.time_stamp
                and self.author_name == other.author_name
                and self.author_email == other.author_email
                and self.configuration == other.configuration
                and self.metadata_content == other.metadata_content
        )

    @classmethod
    def from_json_obj(cls, obj: JSONObject) -> "MetadataInstance":
        assert obj["@"]["type"] == "MetadataInstance"
        check_serialized_version(obj)
        return cls(
            obj["time_stamp"],
            obj["author"],
            obj["author_email"],
            ExtractorConfiguration.from_json_obj(obj["configuration"]),
            obj["metadata_content"]
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
                 initial_metadata_instances: Optional[Iterable[MetadataInstance]] = None):

        self.parameter_set = list()
        self.instances = dict()
        for metadata_instance in initial_metadata_instances or []:
            self.add_metadata_instance(metadata_instance)

    def __iter__(self):
        yield from self.instances.values()

    def add_metadata_instance(self, metadata_instance: MetadataInstance):
        if metadata_instance.configuration not in self.parameter_set:
            self.parameter_set.append(metadata_instance.configuration)
        instance_key = self.parameter_set.index(metadata_instance.configuration)
        self.instances[instance_key] = metadata_instance

    def get_instances(self) -> Generator[MetadataInstance, None, None]:
        yield from self.instances.values()

    def get_configurations(self) -> List[ExtractorConfiguration]:
        return self.parameter_set[:]

    def get_instance_for_configuration_index(self, index: int):
        return self.instances[index]

    def get_instance_for_configuration(self, configuration: ExtractorConfiguration):
        return self.instances[self.parameter_set.index(configuration)]

    def to_json_obj(self) -> JSONObject:
        return {
            "@": dict(
                type="MetadataInstanceSet",
                version=version_string
            ),
            "parameter_set": [
                configuration.to_json_obj()
                for configuration in self.parameter_set
            ],
            "instance_set": {
                instance_key: instance.to_json_obj()
                for instance_key, instance in self.instances.items()
            }
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_obj())

    @classmethod
    def from_json_obj(cls, obj: JSONObject) -> "MetadataInstanceSet":
        assert obj["@"]["type"] == "MetadataInstanceSet"
        check_serialized_version(obj)

        metadata_instance_set = cls()
        metadata_instance_set.parameter_set = [
            ExtractorConfiguration.from_json_obj(json_obj)
            for json_obj in obj["parameter_set"]
        ]
        metadata_instance_set.instances = {
            int(configuration_id): MetadataInstance.from_json_obj(json_obj)
            for configuration_id, json_obj in obj["instance_set"].items()
        }
        return metadata_instance_set

    @classmethod
    def from_json_str(cls, json_str: str) -> "MetadataInstanceSet":
        return cls.from_json_obj(json.loads(json_str))

    def __eq__(self, other: "MetadataInstanceSet"):
        return sorted(self.parameter_set) == sorted(other.parameter_set) \
               and self.instances == other.instances


class Metadata(MappableObject):
    """
    Holds entries for all metadata of a single object.
    Metadata is identified on the first level by its
    format-name, i.e. the extractor-name. For each
    extractor there is a set of configurations and
    associated metadata, i.e. objects that contain
    the extractor result, aka the real metadata.
    """
    def __init__(self,
                 realm: Optional[str] = None,
                 reference: Optional[Reference] = None):

        assert isinstance(realm, (type(None), str))
        assert isinstance(reference, (type(None), Reference))

        super().__init__(realm, reference)
        self.instance_sets: Dict[str, MetadataInstanceSet] = dict()

    def __eq__(self, other):
        return self.instance_sets == other.instance_sets

    @staticmethod
    def get_empty_instance(realm: Optional[str] = None,
                           reference: Optional[Reference] = None):
        return Metadata(realm, reference)

    def purge_impl(self):
        self.instance_sets = dict()

    def get_modifiable_sub_objects_impl(self) -> Iterable[MappableObject]:
        return []

    def extractors(self) -> Generator[str, None, None]:
        yield from self.instance_sets.keys()

    def extractor_runs(self) -> Generator[Tuple[str, MetadataInstanceSet], None, None]:
        yield from self.instance_sets.items()

    def extractor_runs_for_extractor(self, extractor_name: str) -> MetadataInstanceSet:
        return self.instance_sets[extractor_name]

    def add_extractor_run(self,
                          time_stamp: Optional[float],
                          extractor_name: str,
                          author_name: str,
                          author_email: str,
                          configuration: ExtractorConfiguration,
                          metadata_content: JSONObject):

        self.touch()

        instance_set = self.instance_sets.get(
            extractor_name,
            MetadataInstanceSet())

        instance_set.add_metadata_instance(
            MetadataInstance(
                time_stamp if time_stamp is not None else time.time(),
                author_name,
                author_email,
                configuration,
                metadata_content))

        self.instance_sets[extractor_name] = instance_set

    def to_json(self) -> str:
        return json.dumps({
            "@": dict(
                type="Metadata",
                version=version_string
            ),
            "instance_sets": {
                format_name: instance_set.to_json_obj()
                for format_name, instance_set in self.instance_sets.items()
            }
        })

    def init_from_json(self, json_str) -> None:
        obj = json.loads(json_str)
        check_serialized_version(obj)

        assert obj["@"]["type"] == "Metadata"
        for format_name, instance_set_json_obj in obj["instance_sets"].items():
            self.instance_sets[format_name] = \
                MetadataInstanceSet.from_json_obj(instance_set_json_obj)

    @classmethod
    def from_json(cls, json_str: str) -> "Metadata":
        metadata = cls(None)
        metadata.init_from_json(json_str)
        metadata.mapped = True
        metadata.set_unsaved()
        return metadata

    def deepcopy_impl(self,
                      new_mapper_family: Optional[str] = None,
                      new_destination: Optional[str] = None,
                      **kwargs) -> "Metadata":

        copied_metadata = Metadata()
        for extractor_name, instance_set in self.instance_sets.items():
            copied_metadata.instance_sets[extractor_name] = copy.deepcopy(instance_set)
        copied_metadata.write_out(new_destination)
        copied_metadata.purge()
        return copied_metadata
