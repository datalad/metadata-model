import logging

import click
import dataclasses

from tools.metadata_creator.mimic import create_metadata_from_dataset


mdc_logger = logging.getLogger("metadata_creator")


@dataclasses.dataclass
class MDCContext:
    mapper_family: str


@click.group()
@click.pass_context
@click.option("--verbose", is_flag=True, default=False, help="Increase progress output")
@click.option("--quiet", is_flag=True, default=False, help="Do not write progress output")
@click.option("--mapper-family", type=click.Choice(["git", "memory"]), default="git")
def mdc(ctx, verbose, quiet, mapper_family):
    """
    MetaData Creator

    This tool uses the datalad metadata model API and creates
    algorithmically generated metadata structures. This is
    mainly to demonstrate and debug the datalad metadata model
    implementations.

    All metadata is algorithmically created or taken from the
    command arguments. No extractors are executed.

    By default the git-backend is used to persist models, but any
    implemented back can be used. The currently supported backends
    are: `git´ and `memory´.
    """

    if quiet:
        mdc_logger.setLevel(logging.FATAL)
        logging.basicConfig(level=logging.FATAL, format="mdc: %(message)s")

    if verbose:
        mdc_logger.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG, format="mdc: %(message)s")

    ctx.obj = MDCContext(mapper_family=mapper_family)
    mdc_logger.debug(f"context object: {ctx.obj}")


@mdc.command()
@click.pass_context
@click.argument("dataset_path", nargs=1)
@click.argument("realm", nargs=1)
@click.option("-p", "--parameter-set-count", type=int, default=1)
def from_template(ctx, dataset_path, realm, parameter_set_count):
    """
    Create test metadata that mimics the structure of a dataset

    This command will create test metadata the reflects the structure
    of the given dataset. That is, the dataset tree represent the
    dataset containment hierarchy, the UUID set represents the UUIDs
    of the contained datasets and the file trees are modelled after
    the files in the datasets.

    \b
    Usage:
    from-template [DATASET_PATH] [REALM]
    DATASET_PATH: prefix_path of the datalad dataset the should be mimicked
    REALM: realm in which the metadata should be stored
    """

    create_metadata_from_dataset(
        ctx.obj.mapper_family,
        realm,
        dataset_path,
        parameter_set_count)


def main():
    mdc(auto_envvar_prefix="METADATA_CREATOR")


if __name__ == "__main__":
    main()
