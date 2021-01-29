import logging

import click

from .create import create_metadata


MDC_LOGGER = logging.getLogger("metadata_creator")


@click.command()
@click.option("--verbose", is_flag=True, default=False, help="Increase progress output")
@click.option("--quiet", is_flag=True, default=False, help="Do not write progress output")
@click.option("--mapper-family", type=click.Choice(["git", "memory"]), default="git")
@click.argument("realm", nargs=-1)
def mdc(verbose, quiet, mapper_family, realm):
    """
    Create test metadata

    This tools algorithmically creates metadata models and
    maps them onto a backend. The currently supported backends
    are: `git´ and `memory´.
    """
    if quiet:
        MDC_LOGGER.setLevel(logging.FATAL)
        logging.basicConfig(level=logging.FATAL, format="MDC: %(message)s")
    if verbose:
        MDC_LOGGER.setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG, format="MDC: %(message)s")

    ctx.obj = {
        "mapper_family": mapper_family,
        "realm": realm
    }
    MDC_LOGGER.debug(f"context object: {ctx.obj}")

    result = create_metadata(mapper_family, realm)
    print(result)


def main():
    mdc(auto_envvar_prefix="METADATA_CREATOR")


if __name__ == "__main__":
    main()
