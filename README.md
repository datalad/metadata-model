# Datalad Metadata Model

This repository contains the metadata model that datalad and datalad-metalad (will) use
for their metadata.

The model is separated into individual components that can be independently loaded
and saved in order to have a focus-based view on the potentially very large metadata
model instance.

The model defines a Mapper-interface that is used to persist its instances to storage
devices. This allows a multitude of backends that can also be used together, e.g. 
copy from one backend to another.


