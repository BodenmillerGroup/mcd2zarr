try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .mcd2zarr import convert_mcd_to_zarr

__all__ = ["convert_mcd_to_zarr"]
