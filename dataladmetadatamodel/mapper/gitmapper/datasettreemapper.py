
from .objectreference import GitReference, add_tree_reference
from .gitbackend.subprocess import git_ls_tree_recursive, git_save_tree
from .metadatarootrecordmapper import MetadataRootRecordGitMapper
from ..basemapper import BaseMapper
from ..reference import Reference


DATALAD_ROOT_RECORD_NAME = ".datalad_metadata_root_record"


class DatasetTreeGitMapper(BaseMapper):

    def _unmap_metadata_root_record(self, metadata_root_record) -> str:
        return MetadataRootRecordGitMapper(self.realm).unmap(metadata_root_record)

    def _save_dataset_tree(self, node: "TreeNode") -> str:
        dir_entries = []

        if node.value is not None:
            from dataladmetadatamodel.metadatarootrecord import MetadataRootRecord

            assert isinstance(node.value, MetadataRootRecord)
            location = self._unmap_metadata_root_record(node.value)
            dir_entries.append(("100644", "blob", location, DATALAD_ROOT_RECORD_NAME))

        for name, child_node in node.child_nodes.items():
            dir_entries.append(("040000", "tree", self._save_dataset_tree(child_node), name))

        return git_save_tree(self.realm, dir_entries)

    def _map_metadata_root_record(self, location: str) -> "MetadataRootRecord":
        return MetadataRootRecordGitMapper(self.realm).map(
            Reference("git", "MetadataRootRecord", location)
        )

    def map(self, ref: Reference) -> "DatasetTree":
        from dataladmetadatamodel.datasettree import DatasetTree
        from dataladmetadatamodel.treenode import TreeNode

        dataset_tree = DatasetTree("git", self.realm)

        # List all leaf-nodes. Those should only end with the datalad
        # root record-name. Add the hierarchy except the leaf-node,
        # read the metadata root record from the leave node, and
        # add it as value to the hierarchy.
        for line in git_ls_tree_recursive(self.realm, ref.location):

            _, _, location, path = line.split()
            path_element = path.split("/")
            assert path_element[-1] == DATALAD_ROOT_RECORD_NAME
            metadata_root_record = self._map_metadata_root_record(location)

            dataset_path = "/".join(path_element[:-1])
            dataset_tree.add_node_hierarchy(
                dataset_path,
                TreeNode(metadata_root_record),
                allow_leaf_node_conversion=True
            )
        return dataset_tree

    def unmap(self, obj) -> str:
        """
        Save DatasetTree as git tree with DATALAD_ROOT_RECORD_NAME
        nodes for each MetadataRootRecord instance.
        """
        from dataladmetadatamodel.datasettree import DatasetTree

        assert isinstance(obj, DatasetTree)
        dataset_tree_hash = self._save_dataset_tree(obj)
        add_tree_reference(self.realm, GitReference.DATASET_TREE, dataset_tree_hash)
        return dataset_tree_hash
