#!/usr/bin/env python3
import argparse
import os
import numpy as np
import rasterio
from rasterio.enums import ColorInterp

def convert_to_uint8(path_in):
    # Generate output path
    base, ext = os.path.splitext(path_in)
    path_out = f"{base}_uint8{ext}"

    # Read GeoTIFF
    with rasterio.open(path_in) as src:
        profile = src.profile
        data = src.read()  # shape: (bands, height, width), dtype=uint16

        # Save metadata and color info
        src_tags = src.tags()
        src_band_tags = [src.tags(i + 1) for i in range(src.count)]
        src_colorinterp = src.colorinterp

    # Convert from uint16 → uint8 (custom scaling)
    data_float = data.astype(np.float32)

    # Force all values <256 → 0, scale the rest linearly to 0–255
    data_float[data_float < 256] = 0
    data_uint8 = np.clip((data_float / 65535) * 255, 0, 255).astype(np.uint8)

    # Handle nodata properly (preserve nodata mask if present)
    nodata_value = profile.get("nodata", None)
    if nodata_value is not None:
        for b in range(data.shape[0]):
            mask = data[b] == nodata_value
            data_uint8[b][mask] = 0  # set nodata areas to 0

    # Update profile
    profile.update(dtype=rasterio.uint8, count=data_uint8.shape[0])

    # Write GeoTIFF
    with rasterio.open(path_out, 'w', **profile) as dst:
        dst.write(data_uint8)

        # Restore correct band interpretations (NIR, Red, Green, Blue)
        if data_uint8.shape[0] == 4:
            dst.colorinterp = (
                ColorInterp.gray,   # Band 1: NIR
                ColorInterp.red,    # Band 2: Red
                ColorInterp.green,  # Band 3: Green
                ColorInterp.blue    # Band 4: Blue
            )
        elif data_uint8.shape[0] == 3:
            dst.colorinterp = (
                ColorInterp.red,
                ColorInterp.green,
                ColorInterp.blue
            )
        else:
            dst.colorinterp = tuple([ColorInterp.undefined] * data_uint8.shape[0])

        # Add band name metadata (visible in QGIS metadata)
        band_names = ["NIR", "Red", "Green", "Blue"]
        for i, name in enumerate(band_names[:data_uint8.shape[0]], start=1):
            dst.update_tags(i, BAND_NAME=name)

        # Preserve dataset-level and per-band metadata
        dst.update_tags(**src_tags)
        for i, band_tags in enumerate(src_band_tags, start=1):
            if band_tags:
                dst.update_tags(i, **band_tags)

    print(f"✅ Converted file saved as: {path_out}")


def main():
    parser = argparse.ArgumentParser(description="Convert uint16 GeoTIFF to uint8")
    parser.add_argument("--path_in", required=True, help="Path to the input GeoTIFF")
    args = parser.parse_args()

    convert_to_uint8(args.path_in)


if __name__ == "__main__":
    main()

