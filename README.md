# Datalad Metadata Model

This repository contains the metadata model that datalad and datalad-metalad (will) use
for their metadata.

The model is separated into individual components that can be independently loaded
and saved in order to have a focus-based view on the potentially very large metadata
model instance (an application of the "proxy design pattern").

The implementation is devided into a user facing API-layer and a storage layer. Both
are independent from each other (as long as the model does not change).
The API layer defines an abstract data type, which represents the metadata model. The
storage layer is responsible for persisting the model instance.

The two layers communicate through a defined interface. This allows for the use of multiple different
storage layers with the same model instance. This can be even done in parallel, for example, if you
want to copy a model from one storage layer to another storage layer. It also allows
for the independent development of storage backends


