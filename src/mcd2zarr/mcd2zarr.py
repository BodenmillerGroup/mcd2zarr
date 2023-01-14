from pathlib import Path
from typing import Optional
from warnings import warn

import numpy as np
import zarr
from ome_zarr.format import CurrentFormat, format_from_version
from ome_zarr.writer import write_image
from readimc import MCDFile


def convert_mcd_to_zarr(
    mcd_file: Path,
    zarr_file: Path,
    zarr_version: Optional[str] = None,
    ome_zarr_version: Optional[str] = None,
) -> None:
    if ome_zarr_version is not None:
        ome_zarr_format = format_from_version(ome_zarr_version)
    else:
        ome_zarr_format = CurrentFormat()
    with MCDFile(mcd_file) as f:
        slide_group_names = [
            f"S{slide.id:02d}_{slide.description}" for slide in f.slides
        ]
        zarr_group: zarr.Group = zarr.open(
            zarr_file, mode="w", zarr_version=zarr_version
        )
        zarr_group.attrs["mcd_file"] = mcd_file.name
        zarr_group.attrs["mcd_schema"] = f.metadata
        zarr_group.attrs["slide_groups"] = slide_group_names
        for slide, slide_group_name in zip(f.slides, slide_group_names):
            acquisition_group_names = [
                f"A{acquisition.id:02d}_{acquisition.description}"
                for acquisition in slide.acquisitions
            ]
            panorama_group_names = [
                f"P{panorama.id:02d}_{panorama.description}"
                for panorama in slide.panoramas
            ]
            slide_group = zarr_group.create_group(slide_group_name, overwrite=True)
            slide_group.attrs["slide_metadata"] = slide.metadata
            slide_group.attrs["acquisition_groups"] = acquisition_group_names
            slide_group.attrs["panorama_groups"] = panorama_group_names
            for acquisition, acquisition_group_name in zip(
                slide.acquisitions, acquisition_group_names
            ):
                acquisition_img = f.read_acquisition(acquisition)
                acquisition_group = slide_group.create_group(
                    acquisition_group_name, overwrite=True
                )
                acquisition_group.attrs["acquisition_metadata"] = acquisition.metadata
                acquisition_group.attrs["omero"] = {
                    "name": f"{mcd_file.name} (A{acquisition.id:02d})",
                    "channels": [
                        {
                            "active": False,
                            "color": "FFFFFF",
                            "label": channel_label,
                            "window": {
                                "start": 0.0,
                                "end": float(channel_max),
                                "min": float(np.finfo(acquisition_img.dtype).min),
                                "max": float(np.finfo(acquisition_img.dtype).max),
                            },
                        }
                        for channel_label, channel_max in zip(
                            acquisition.channel_labels,
                            np.amax(acquisition_img, axis=(1, 2)),
                        )
                    ],
                    "rdefs": {"model": "greyscale"},
                }
                write_image(
                    acquisition_img,
                    acquisition_group,
                    scaler=None,
                    fmt=ome_zarr_format,
                    axes=["c", "y", "x"],
                )  # TODO coordinate_transformations
                before_ablation_img = f.read_before_ablation_image(acquisition)
                acquisition_group.attrs["has_before_ablation_image"] = (
                    before_ablation_img is not None
                )
                if before_ablation_img is not None:
                    before_ablation_group = acquisition_group.create_group(
                        "before_ablation_image", overwrite=True
                    )
                    write_image(
                        before_ablation_img,
                        before_ablation_group,
                        scaler=None,
                        fmt=ome_zarr_format,
                        axes=["y", "x"],
                    )  # TODO coordinate_transformations
                after_ablation_img = f.read_after_ablation_image(acquisition)
                acquisition_group.attrs["has_after_ablation_image"] = (
                    after_ablation_img is not None
                )
                if after_ablation_img is not None:
                    after_ablation_group = acquisition_group.create_group(
                        "after_ablation_image", overwrite=True
                    )
                    write_image(
                        after_ablation_img,
                        after_ablation_group,
                        scaler=None,
                        fmt=ome_zarr_format,
                        axes=["y", "x"],
                    )  # TODO coordinate_transformations
            for panorama, panorama_group_name in zip(
                slide.panoramas, panorama_group_names
            ):
                panorama_img = f.read_panorama(panorama)
                if panorama_img.ndim == 2:
                    panorama_axes = ["y", "x"]
                elif panorama_img.ndim == 3:
                    panorama_img = np.moveaxis(panorama_img, -1, 0)
                    panorama_axes = ["c", "y", "x"]
                else:
                    warn(
                        f"Cannot guess axes for {panorama_img.ndim}-dimensional "
                        f"panorama {panorama.id} ('{panorama.description}'); skipping"
                    )
                    continue
                panorama_group = slide_group.create_group(
                    panorama_group_name, overwrite=True
                )
                panorama_group.attrs["panorama_metadata"] = panorama.metadata
                write_image(
                    panorama_img,
                    panorama_group,
                    scaler=None,
                    fmt=ome_zarr_format,
                    axes=panorama_axes,
                )  # TODO coordinate_transformations
