[![Build status](https://ci.appveyor.com/api/projects/status/tjkich0nqkjuotxb?svg=true)](https://ci.appveyor.com/project/mih/metadata-model)
[![codecov](https://codecov.io/gh/datalad/metadata-model/branch/main/graph/badge.svg?token=YBU774L1A7)](https://codecov.io/gh/datalad/metadata-model)
[![PyPI version](https://badge.fury.io/py/datalad-metadata-model.svg)](https://badge.fury.io/py/datalad-metadata-model)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/datalad/metadata-model?include_prereleases&label=github%20release&style=flat-square)

# Datalad Metadata Model

This software implements the metadata model that datalad and datalad-metalad will
use in the future (datalad-metalad>=0.3.0) to handle metadata.

#### Model Elements (the model layer)
The metadata model is defined by the API of the top-level
classes. Those are:

- `MetadataRootRecord` -- holds top-level metadata information for a single
version of a datalad dataset

- `UUIDSet` -- holds metadata root records for a set of datasets that are
 identified by their UUIDs and their version.

- `TreeVersionList` -- holds metadata root records and a sub-dataset tree for a
dataset version and its sub-datasets

- `Metadata` -- represents metadata for a single item, i.e. dataset or file.
Metadata is associated with extractor names and extraction parameters.

- `DatasetTree` -- a representation of the sub-dataset hierarchy of a dataset

- `FileTree` -- a representation of the file-tree of a dataset

- ... 

Because of the large size of some datalad-datasets, e.g. tens of thousands of
sub-datasets and hundres of millions of files, the implementation allows
focus-based operations on individual parts of the potentially very large 
metadata model. The implementation uses the proxy-pattern, that means, it
 loads, modifies, and saves only the minimal necessary model elements that are
 necessary to operate on the metadata-information that
 the user is interested in.

#### Storage layer

The model elements have to be persisted on a storage backend.
 How the model is mapped on storage backends is defined by the
storage layer, that is to a large degree independent of the model layer. 
The intention is to support multiple storage backends in the past.

Currently only one storage backend is supported:

- `git-mapping` -- a storage backend that stores a metadata model in a
git repository. The model objects are stored outside of existing branches.
They are referenced by `datalad`-specific git-references under `refs/datalad/*`
