from pathlib import Path
from typing import Optional

import click

from .mcd2zarr import convert_mcd_to_zarr


@click.command(name="mcd2zarr", help="Convert MCD files to Zarr")
@click.option("--zarr-version", "zarr_version", help="Zarr version")
@click.option("--ome-zarr-version", "ome_zarr_version", help="OME-Zarr version")
@click.argument(
    "mcd_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.argument(
    "zarr_file", type=click.Path(dir_okay=False, path_type=Path), required=False
)
@click.version_option()
def main(
    mcd_file: Path,
    zarr_file: Optional[Path],
    zarr_version: Optional[str],
    ome_zarr_version: Optional[str],
) -> None:
    if zarr_file is None:
        zarr_file = mcd_file.with_suffix(".zarr")
    convert_mcd_to_zarr(
        mcd_file,
        zarr_file,
        zarr_version=zarr_version,
        ome_zarr_version=ome_zarr_version,
    )


if __name__ == "__main__":
    main()
