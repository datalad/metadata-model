import logging


from dataladmetadatamodel.mapper.gitmapper.objectreference import flush_object_references

from tools.metadata_creator.mrrcreator import create_mrrs_from_dataset
from tools.metadata_creator.treeversionlistcreator import create_tree_version_list_for_mrrs
from tools.metadata_creator.uuidsetcreator import create_uuid_set_for_mrrs


mdc_logger = logging.getLogger("metadata_creator")


def create_metadata_from_dataset(mapper: str,
                                 realm: str,
                                 dataset_path: str,
                                 parameter_set_count: int
                                 ):

    metadata_root_records = create_mrrs_from_dataset(
        mapper,
        realm,
        dataset_path,
        parameter_set_count)

    uuid_set = create_uuid_set_for_mrrs(
        mapper,
        realm,
        metadata_root_records)
    mdc_logger.info(f"saving uuid set: {uuid_set}")
    uuid_set.save()
    mdc_logger.info(f"done saving uuid set: {uuid_set}")

    tree_version_list = create_tree_version_list_for_mrrs(
        mapper,
        realm,
        metadata_root_records)
    mdc_logger.info(f"saving tree version list: {tree_version_list}")
    tree_version_list.save()
    mdc_logger.info(f"done saving tree version list: {tree_version_list}")

    flush_object_references(Path(realm))
