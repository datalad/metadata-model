import copy
import json
import time
from typing import Dict, Generator, Iterable, List, Optional, Tuple

from . import JSONObject
from .connector import ConnectedObject
from .mapper import get_mapper
from .mapper.reference import Reference
from .metadatasource import MetadataSource, LocalGitMetadataSource


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
                 metadata_source: MetadataSource):

        self.time_stamp = time_stamp
        self.author_name = author_name
        self.author_email = author_email
        self.configuration = configuration
        self.metadata_source = metadata_source

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
            "metadata_source": self.metadata_source.to_json_obj()
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_json_obj())

    def __eq__(self, other):
        return (
                self.time_stamp == other.time_stamp
                and self.author_name == other.author_name
                and self.author_email == other.author_email
                and self.configuration == other.configuration
                and self.metadata_source == other.metadata_source
        )

    @classmethod
    def from_json_obj(cls, obj: JSONObject) -> "MetadataInstance":
        assert obj["@"]["type"] == "MetadataInstance"
        assert obj["@"]["version"] == "1.0"
        return cls(
            obj["time_stamp"],
            obj["author"],
            obj["author_email"],
            ExtractorConfiguration.from_json_obj(obj["configuration"]),
            MetadataSource.from_json_obj(obj["metadata_source"])
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
                version="1.0"
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
        assert obj["@"]["version"] == "1.0"

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
                 realm: str):

        super().__init__()
        self.mapper_family = mapper_family
        self.realm = realm
        self.instance_sets: Dict[str, MetadataInstanceSet] = dict()

    def to_json(self) -> str:
        return json.dumps({
            "@": dict(
                type="Metadata",
                version="1.0"
            ),
            "mapper_family": self.mapper_family,
            "realm": self.realm,
            "instance_sets": {
                format_name: instance_set.to_json_obj()
                for format_name, instance_set in self.instance_sets.items()
            }
        })

    def save(self) -> Reference:
        self.un_touch()
        return Reference(
            self.mapper_family,
            self.realm,
            "Metadata",
            get_mapper(
                self.mapper_family,
                "Metadata")(self.realm).unmap(self))

    def extractors(self) -> Generator[str, None, None]:
        yield from self.instance_sets.keys()

    def extractor_runs(self) -> Generator[Tuple[str, MetadataInstanceSet], None, None]:
        yield from self.instance_sets.items()

    def add_extractor_run(self,
                          time_stamp: Optional[float],
                          extractor_name: str,
                          author_name: str,
                          author_email: str,
                          configuration: ExtractorConfiguration,
                          metadata_source: MetadataSource):

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
                metadata_source))

        self.instance_sets[extractor_name] = instance_set

    @classmethod
    def from_json(cls, json_str: str):
        obj = json.loads(json_str)
        assert obj["@"]["type"] == "Metadata"
        assert obj["@"]["version"] == "1.0"

        metadata = cls(
            obj["mapper_family"],
            obj["realm"]
        )

        for format_name, instance_set_json_obj in obj["instance_sets"].items():
            metadata.instance_sets[format_name] = \
                MetadataInstanceSet.from_json_obj(instance_set_json_obj)

        return metadata

    def deepcopy(self,
                 new_mapper_family: Optional[str] = None,
                 new_realm: Optional[str] = None,
                 new_content_repository: Optional[str] = None) -> "Metadata":

        # TODO: pass new_content_repository through from above, because
        #  the following line will not work, if other backend than git
        #  are supported, and it might not be what is intended.
        new_content_repository = new_content_repository or new_realm

        new_mapper_family = new_mapper_family or self.mapper_family
        new_realm = new_realm or self.realm

        copied_metadata = Metadata(new_mapper_family, new_realm)
        for extractor_name, instance_set in self.instance_sets.items():

            # copy the instance set, i.e. the model object
            copied_metadata.instance_sets[extractor_name] = \
                copy.deepcopy(instance_set)

            # copy all referenced objects that should be copied, currently
            # those are git-blobs stored in the local git repository, i.e.
            # objects that are managed by LocalGitMetadataSource.
            # TODO: new_content_repository is not nice, since it is specific
            #  to the LocalGitMetadataSource. This
            #  probably has to be done nicer.
            if new_content_repository is not None:
                for metadata_instance in instance_set.get_instances():
                    if isinstance(metadata_instance, LocalGitMetadataSource):
                        metadata_instance.copy_object_to(new_content_repository)

            del instance_set

        return copied_metadata

    def __eq__(self, other):
        return self.instance_sets == other.instance_sets
