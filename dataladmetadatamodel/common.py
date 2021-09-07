"""
Commonly used functionality
"""
import time
from typing import (
    Optional,
    Tuple
)
from uuid import UUID

from dataladmetadatamodel.connector import Connector
from dataladmetadatamodel.datasettree import DatasetTree
from dataladmetadatamodel.filetree import FileTree
from dataladmetadatamodel.metadata import Metadata
from dataladmetadatamodel.metadatapath import MetadataPath
from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord
from dataladmetadatamodel.uuidset import UUIDSet
from dataladmetadatamodel.versionlist import (
    TreeVersionList,
    VersionList
)
from dataladmetadatamodel.mapper.reference import Reference


def get_top_level_metadata_objects(
        mapper_family: str,
        realm: str
        ) -> Tuple[Optional[TreeVersionList], Optional[UUIDSet]]:

    """
    Load the two top-level metadata elements from a realm, i.e.
    the tree version list and the uuid list.

    We do this be creating references from known locations
    in the mapper family and loading the referenced objects.
    """
    from dataladmetadatamodel.mapper import (
        get_uuid_set_location,
        get_tree_version_list_location)

    tree_version_list_connector = Connector.from_reference(
        Reference(
            mapper_family,
            realm,
            "TreeVersionList",
            get_tree_version_list_location(mapper_family)))

    uuid_set_connector = Connector.from_reference(
        Reference(
            mapper_family,
            realm,
            "UUIDSet",
            get_uuid_set_location(mapper_family)))

    try:
        return (
            tree_version_list_connector.load_object(),
            uuid_set_connector.load_object())
    except RuntimeError:
        return None, None


def get_top_nodes_and_metadata_root_record(
        mapper_family: str,
        realm: str,
        dataset_id: UUID,
        primary_data_version: str,
        dataset_tree_path: MetadataPath,
        auto_create: Optional[bool] = False):

    """
    Return the top nodes and metadata root record for a given dataset id
    and a given dataset version.

    If auto_create is True, create missing entries for the given dataset
    version, down to and including the metadata root record with empty
    dataset metadata and an empty file-tree connected to it.

    If auto_create is False and any of the elements: uuid set, version tree
    list, or metadata root record does not exist, (None, None, None) is
    returned.

    If you want to preserve any changes, are created metadata objects,
    you have to save the returned objects and flush the realm
    """
    tree_version_list, uuid_set = get_top_level_metadata_objects(
        mapper_family,
        realm)

    if tree_version_list is None and auto_create:
        tree_version_list = TreeVersionList(mapper_family, realm)

    if uuid_set is None and auto_create:
        uuid_set = UUIDSet(mapper_family, realm)

    if uuid_set is None or tree_version_list is None:
        return None, None, None

    if dataset_id in uuid_set.uuids():
        uuid_version_list = uuid_set.get_version_list(dataset_id)
    else:
        if auto_create is False:
            return None, None, None
        uuid_version_list = VersionList(mapper_family, realm)
        uuid_set.set_version_list(dataset_id, uuid_version_list)

    # Get the dataset tree
    if primary_data_version in tree_version_list.versions():
        time_stamp, dataset_tree = tree_version_list.get_dataset_tree(
            primary_data_version)
    else:
        if auto_create is False:
            return None, None, None
        time_stamp = str(time.time())
        dataset_tree = DatasetTree(mapper_family, realm)
        tree_version_list.set_dataset_tree(
            primary_data_version,
            time_stamp,
            dataset_tree)

    if dataset_tree_path not in dataset_tree:
        if auto_create is False:
            return None, None, None

        dataset_level_metadata = Metadata(mapper_family, realm)
        file_tree = FileTree(mapper_family, realm)
        metadata_root_record = MetadataRootRecord(
            mapper_family,
            realm,
            dataset_id,
            primary_data_version,
            Connector.from_object(dataset_level_metadata),
            Connector.from_object(file_tree))
        dataset_tree.add_dataset(dataset_tree_path, metadata_root_record)
    else:
        metadata_root_record = dataset_tree.get_metadata_root_record(
            dataset_tree_path)

    uuid_version_list.set_versioned_element(
        primary_data_version,
        str(time.time()),
        dataset_tree_path,
        metadata_root_record)

    return tree_version_list, uuid_set, metadata_root_record
