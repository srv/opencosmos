import argparse
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
import numpy as np
from PIL import Image

def georeference_png_to_geotiff(png_path, geotiff_path, pixel1, map1, pixel2, map2, crs="EPSG:4326"):
    """
    Georeference a PNG image using two control points and save as GeoTIFF.

    Parameters
    ----------
    png_path : str
        Path to input PNG image.
    geotiff_path : str
        Path to output GeoTIFF.
    pixel1, pixel2 : tuple (row, col)
        Pixel indices of the two control points in the image.
    map1, map2 : tuple (Y, X)
        Map coordinates of the two control points.
        - For EPSG:4326 → (lat, lon) in degrees
        - For projected CRS → (northing, easting) in meters
    crs : str
        Coordinate reference system (default WGS84 EPSG:4326)
    """

    # Unpack pixel and map coordinates
    row1, col1 = pixel1
    y1, x1 = map1
    row2, col2 = pixel2
    y2, x2 = map2

    # Load PNG as array
    img = Image.open(png_path)
    arr = np.array(img)

    # Compute pixel size
    pixel_width = (x2 - x1) / (col2 - col1)
    pixel_height = (y2 - y1) / (row2 - row1)

    # Compute top-left corner of pixel (0,0)
    x_origin = x1 - (col1 + 0.5) * pixel_width
    y_origin = y1 - (row1 + 0.5) * pixel_height

    # Affine transform
    transform = from_origin(
        x_origin,
        y_origin,
        pixel_width,
        -pixel_height
    )

    # Handle grayscale vs RGB(A)
    if arr.ndim == 2:
        count = 1
    else:
        arr = np.transpose(arr, (2, 0, 1))
        count = arr.shape[0]

    # Write GeoTIFF
    with rasterio.open(
        geotiff_path,
        "w",
        driver="GTiff",
        height=arr.shape[-2],
        width=arr.shape[-1],
        count=count,
        dtype=arr.dtype,
        crs=CRS.from_string(crs),
        transform=transform,
    ) as dst:
        if count == 1:
            dst.write(arr, 1)
        else:
            dst.write(arr)

    print(f"GeoTIFF written to {geotiff_path}")


def main():
    parser = argparse.ArgumentParser(description="Georeference a PNG using two control points")
    parser.add_argument("png_path", help="Input PNG image")
    parser.add_argument("geotiff_path", help="Output GeoTIFF path")
    parser.add_argument("--crs", default="EPSG:4326", help="CRS of the map coordinates")
    args = parser.parse_args()

    # --- Define control points here ---
    # Example for WGS84 degrees
    pixel1 = (200, 100)        # (row, col)
    map1   = (45.678, 12.345)  # (lat, lon)
    pixel2 = (800, 600)
    map2   = (45.670, 12.355)

    # Example for UTM meters (EPSG:25831)
    # pixel1 = (200, 100)
    # map1   = (4580000, 430000)  # (northing, easting)
    # pixel2 = (800, 600)
    # map2   = (4579400, 431500)
    # crs    = "EPSG:25831"

    georeference_png_to_geotiff(
        args.png_path,
        args.geotiff_path,
        pixel1, map1,
        pixel2, map2,
        crs=args.crs
    )


if __name__ == "__main__":
    main()
