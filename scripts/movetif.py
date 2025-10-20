#!/usr/bin/env python3
import argparse
import rasterio
from rasterio.transform import Affine
import os

def move_geotiff(input_path, output_path, north_shift, east_shift):
    """
    Move a GeoTIFF by given distances (in meters).
    Positive north_shift moves north (up),
    Positive east_shift moves east (right).
    """
    with rasterio.open(input_path) as src:
        transform = src.transform
        
        # Modify the affine transform: shift origin
        moved_transform = transform * Affine.translation(east_shift / transform.a, -north_shift / transform.e)
        
        # Copy metadata and update transform
        meta = src.meta.copy()
        meta.update(transform=moved_transform)
        
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(src.read())

    print(f"✅ Moved {os.path.basename(input_path)} by ({north_shift} m north, {east_shift} m east)")
    print(f"💾 Saved as: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Move a GeoTIFF file north/east by given distances in meters."
    )
    parser.add_argument("--input", help="Input GeoTIFF file (.tif)")
    parser.add_argument("--output", help="Output GeoTIFF file (.tif)")
    parser.add_argument("--north", type=float, default=0.0, help="Shift north (meters, positive = north)")
    parser.add_argument("--east", type=float, default=0.0, help="Shift east (meters, positive = east)")

    args = parser.parse_args()

    move_geotiff(args.input, args.output, args.north, args.east)

if __name__ == "__main__":
    main()

