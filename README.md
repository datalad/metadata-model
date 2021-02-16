# Datalad Metadata Model

This repository contains the metadata model that datalad and datalad-metalad (will) use
for their metadata.

The model is separated into individual components that can be independently loaded
and saved in order to have a focus-based view on the potentially very large metadata
model instance (an application of the "proxy design pattern").

The implementation is divided into a user facing API-layer and a storage layer. Both
are independent from each other (as long as the model does not change).
The API layer defines an abstract data type, which represents the metadata model. The
storage layer is responsible for persisting the model instance.

The two layers communicate through a defined interface. This allows for the use of multiple different
storage layers with the same model instance. This can be even done in parallel, for example, if you
want to copy a model from one storage layer to another storage layer. It also allows
for the independent development of storage backends


# Test it with datalad-metalad

There is a datalad-metalad (aka metalad) fork, i.e. `https://github.com/christian-monch/datalad-metalad` with the branch "metadata_model".
This branch uses the metadata model to operate on metadata.

Currently the metadata_model branch of datalad-metalad implements the following commands
based on the model:

 - meta-dump
 - ... (more to come)
 
Consequently there is also a repository, that contains "test"
metadata (which has been created with the mdc-tool in this distribution).

 
## Installation instructions

(These instructions were tested on Debian 10)
Create a virtual environment, activate it, and upgrade pip, e.g.:

```
python3 -m venv ~/venv/datalad-metadata-model
source ~/venv/datalad-metadata-model/bin/activate
pip install --upgrade pip
```

Clone datalad-metalad and checkout the branch "metadata_model".

```
git clone https://github.com/christian-monch/datalad-metalad
cd datalad-metalad
git checkout metadata_model
```

Install the checked out version of metalad, i.e.
```
pip install -r requirements.txt
```

Invoking `datalad meta-dump` should now output:
```
[WARNING] No git-mapped datalad metadata model found in: .
```


Now, clone the demo-metadata repository into a directory
of your choice, change into it and fetch all remote references

```
git clone https://github.com/christian-monch/datalad-metadata-demo-2.git
```

Change into the directory and fetch some remote references

```
cd datalad-metadata-demo-2
git fetch origin refs/datalad/dataset-tree-version-list:refs/datalad/dataset-tree-version-list
git fetch origin refs/datalad/dataset-uuid-set:refs/datalad/dataset-uuid-set
git fetch origin refs/datalad/object-references/dataset-tree:refs/datalad/object-references/dataset-tree
git fetch origin refs/datalad/object-references/file-tree:refs/datalad/object-references/file-tree
git fetch origin refs/datalad/object-references/metadata:refs/datalad/object-references/metadata
```

## Invocation

Now you are all set to give it a try. Execute:
```
datalad -f json_pp meta-dump -r
```

That should output a few JSON objects describing datasets and files.


(The metadata was created with the "mdc" tool that comes with the datalad-metadata-model package. The dataset
hierarchy and file names are taken from a local clone of the datasets.datalad.org dataset.)
