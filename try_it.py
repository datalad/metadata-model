from uuid import UUID

from model.connector import Connector
from model.filetree import FileTree
from model.metadata import Metadata, ExtractorConfiguration, MetadataInstance
from model.text import Text
from model.uuidset import UUIDSet
from model.versionlist import VersionList
from model.mapper.reference import Reference


MAPPER_FAMILY = "git"
REALM = "/home/cristian/tmp/mod_1"


uuid_0 = UUID("00000000000000000000000000000000")
uuid_1 = UUID("00000000000000000000000000000001")
uuid_2 = UUID("00000000000000000000000000000002")


try_metadata_objects = True
try_tree = True
try_read = True
try_write = False


if try_metadata_objects:
    ec1 = ExtractorConfiguration(
        "1.0",
        {
            "param_1": "1.1",
            "param_2": "2.1",
            "param_3": "3.1",
            "param_4": "4.1",
        }
    )

    ec2 = ExtractorConfiguration(
        "1.0",
        {
            "param_1": "1.2",
            "param_2": "2.2",
            "param_3": "3.2",
            "param_4": "4.2",
        }
    )

    ec3 = ExtractorConfiguration(
        "1.0",
        {
            "param_1": "1.3",
            "param_2": "2.3",
            "param_3": "3.3",
            "param_4": "4.3",
        }
    )

    mi1 = MetadataInstance(
        "01:00:00",
        "x y",
        "x.y@mail.com",
        ec1,
        "source for blob 1"
    )

    mi2 = MetadataInstance(
        "02:00:00",
        "x y",
        "x.y@mail.com",
        ec2,
        "source for blob 2"
    )

    mi3 = MetadataInstance(
        "03:00:00",
        "x y",
        "x.y@mail.com",
        ec3,
        "source for blob 3"
    )

    m1 = Metadata(
        MAPPER_FAMILY,
        REALM,
        {"core-extractor": {mi1, mi2, mi3}}
    )

    x = m1.to_json()

    print(m1)
    print(x)

    m2 = Metadata.from_json(x)

    print(m2)

    print(m1 == m2)

    if not try_tree:
        exit(0)


if try_tree:

    paths = [
        "a.1/b.1/c.1",
        "a.1/b.1/c.2",
        "a.1/b.1/c.3",
        "a.1/b.1/c.4",
        "a.1/b.2/c.1",
        "a.2/b.2/c.1",
        "a.2/b.2/c.2",
    ]

    ft = FileTree(MAPPER_FAMILY, REALM)
    for path in paths:
        ft.add_metadata(path, m1)
    reference = ft.save()
    print(reference)

    exit(0)



if try_read:

    # Read an object hierarchy
    c = Connector.from_reference(
        Reference(
            MAPPER_FAMILY,
            "UUIDSet",
            "refs/develop/dataset-set"
        )
    )

    loaded_uuid_set: UUIDSet = c.load(MAPPER_FAMILY, REALM)
    version_list_uuid_0 = loaded_uuid_set.get_version_list(uuid_0)
    mrr = version_list_uuid_0.get_metadata_root_record("pd-version-1.1")

    print(loaded_uuid_set)
    print(mrr)

    exit(0)


if try_write:

    # Save an in-memory create object hierarchy
    MetadataRootRecord = Text

    version_list_1 = VersionList(MAPPER_FAMILY, REALM)
    version_list_1.set_metadata_root_record("pd-version-1.1", "10:00:00", "/uuid-1", Text("metadata-for pd-version-1.1"))
    version_list_1.set_metadata_root_record("pd-version-1.2", "12:02:00", "/uuid-1", Text("metadata-for pd-version-1.2"))

    version_list_2 = VersionList(MAPPER_FAMILY, REALM)
    version_list_2.set_metadata_root_record("pd-version-2.1", "20:00:00", "/uuid-2", Text("metadata-for pd-version-2.1"))
    version_list_2.set_metadata_root_record("pd-version-2.2", "22:02:00", "/uuid-2", Text("metadata-for pd-version-2.2"))

    uuid_set = UUIDSet(MAPPER_FAMILY, REALM)
    uuid_set.set_version_list(uuid_0, version_list_1)
    uuid_set.set_version_list(uuid_1, version_list_2)

    reference = uuid_set.save()
    print(reference)

    exit(0)
