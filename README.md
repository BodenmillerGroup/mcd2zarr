# mcd2zarr

Command line tool to convert MCD files to Zarr

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install mcd2zarr:

```
pip install mcd2zarr
```

## Usage

Call `mcd2zarr` on the command line:

```
> mcd2zarr --help
Usage: mcd2zarr [OPTIONS] MCD_FILE [ZARR_FILE]

  Convert MCD files to Zarr

Options:
  --zarr-version TEXT      Zarr version
  --ome-zarr-version TEXT  OME-Zarr version
  --version                Show the version and exit.
  --help                   Show this message and exit.
```

## Zarr format

MCD file contents are extracted into the following Zarr structure:

```
myfile.zarr
├── .zattrs  (mcd_file, mcd_schema, slide_groups)
├── .zgroups
│
├── S01_SlideDescription01
├── S02_SlideDescription02
├── ...
└── Snn_SlideDescriptionNN
    ├── .zattrs  (slide_metadata, acquisition_groups, panorama_groups)
    ├── .zgroups
    │
    ├── Ann_AcquisitionDescriptionNN
    ├── A02_AcquisitionDescription02
    ├── ...
    ├── Ann_AcquisitionDescriptionNN  (in OME-Zarr format)
    │   ├── .zattrs  (acquisition_metadata, has_before_ablation_image, has_after_ablation_image)
    │   ├── .zgroups
    │   │
    │   ├── before_ablation_image  (optional, in OME-Zarr format)
    |   |   ├── .zattrs
    |   |   └── .zgroups
    │   │
    │   └── after_ablation_image (optional, in OME-Zarr format)
    |       ├── .zattrs
    |       └── .zgroups
    │
    ├── P01_PanoramaDescription01
    ├── P02_PanoramaDescription02
    ├── ...
    └── Pnn_PanoramaDescriptionNN  (in OME-Zarr format)
        ├── .zattrs  (panorama_metadata)
        └── .zgroups
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://github.com/BodenmillerGroup/mcd2zarr/blob/main/LICENSE)
