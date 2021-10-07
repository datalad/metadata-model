# Datalad Metadata Model

This repository contains the metadata model that datalad and datalad-metalad 
(will) use for their metadata.

The model is separated into individual components that can be independently
loaded  and saved in order to have a focus-based view on the potentially very
large metadata model instance (an application of the "proxy design pattern").

Currently the model elements are stored in git-repositories.
