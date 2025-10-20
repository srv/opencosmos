import argparse
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
import numpy as np
from PIL import Image
from pyproj import Transformer

Image.MAX_IMAGE_PIXELS = None


def georeference_png_to_geotiff(
    mosaic_path, out_path, top_left_lat, top_left_lon,
    pixel_size_x, pixel_size_y, crs="EPSG:25831"
):
    """
    Georeferences a PNG mosaic using known top-left corner position and pixel size.

    Args:
        mosaic_path: Path to input PNG image.
        out_path: Path to output GeoTIFF.
        top_left_lat: Latitude of top-left corner.
        top_left_lon: Longitude of top-left corner.
        pixel_size_x: Pixel size in meters (E-W direction).
        pixel_size_y: Pixel size in meters (N-S direction, usually positive).
        crs: Output CRS (e.g. EPSG:25831).
    """
    # Convert top-left lat/lon to projected CRS (e.g. UTM)
    transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    x_origin, y_origin = transformer.transform(top_left_lon, top_left_lat)

    # Load image
    img = Image.open(mosaic_path)
    arr = np.array(img)

    # Rasterio expects transform from top-left corner
    transform = from_origin(x_origin, y_origin, pixel_size_x, pixel_size_y)

    if arr.ndim == 2:
        count = 1
    else:
        arr = np.transpose(arr, (2, 0, 1))
        count = arr.shape[0]

    # Write GeoTIFF
    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=arr.shape[-2],
        width=arr.shape[-1],
        count=count,
        dtype=arr.dtype,
        crs=CRS.from_string(crs),
        transform=transform,
    ) as dst:
        dst.write(arr if count > 1 else arr, 1 if count == 1 else None)

    print(f"✅ GeoTIFF written to {out_path}")
    print(f"   Top-left corner (lat/lon): ({top_left_lat}, {top_left_lon})")
    print(f"   Pixel size: {pixel_size_x}m (x), {pixel_size_y}m (y)")
    print(f"   CRS: {crs}")


def main():
    parser = argparse.ArgumentParser(description="Georeference PNG using known pixel size and top-left corner lat/lon")
    parser.add_argument("--mosaic_path", required=True, help="Path to PNG mosaic")
    parser.add_argument("--out_path", required=True, help="Output GeoTIFF path")
    parser.add_argument("--top_left_lat", type=float, required=True, help="Latitude of top-left corner")
    parser.add_argument("--top_left_lon", type=float, required=True, help="Longitude of top-left corner")
    parser.add_argument("--pixel_size_x", type=float, required=True, help="Pixel size in meters (X direction)")
    parser.add_argument("--pixel_size_y", type=float, required=True, help="Pixel size in meters (Y direction, positive number)")
    parser.add_argument("--crs", default="EPSG:25831", help="Output CRS (default: EPSG:25831)")
    args = parser.parse_args()

    georeference_png_to_geotiff(
        args.mosaic_path,
        args.out_path,
        args.top_left_lat,
        args.top_left_lon,
        args.pixel_size_x,
        args.pixel_size_y,
        crs=args.crs
    )


if __name__ == "__main__":
    main()

