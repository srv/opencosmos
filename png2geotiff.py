import argparse
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
import numpy as np
from PIL import Image
import yaml
from pyproj import Transformer
from cola2_lib.utils.ned import NED

Image.MAX_IMAGE_PIXELS = None

"""CALL

python png2geotiff.py 
    --mosaic_path path/to/mosaic.png          # Input PNG mosaic image
    --out_path path/to/out.tif                # Output GeoTIFF filename
    --yaml1 path/to/first.yaml                # First image YAML (HM)
    --yaml2 path/to/second.yaml               # Second image YAML (HM)
    --pixel1 100 200                          # Pixel coordinates (row,col) of first reference image in PNG
    --pixel2 500 800                          # Pixel coordinates (row,col) of second reference image in PNG
    --ned_origin_lat 39.5775                  # Latitude of the ROS NED origin (decimal degrees)
    --ned_origin_lon 2.3515                   # Longitude of the ROS NED origin (decimal degrees)
    --crs EPSG:25831                           # CRS for output GeoTIFF (UTM Zone 31N)

python3 png2geotiff.py --mosaic_path ../data/mosaics/stelm/3/mosaic_x2.png --out_path ../data/mosaics/stelm/3/mosaic_x2.tif --yaml1 ../data/mosaics/stelm/3/12.yaml --yaml2 ../data/mosaics/stelm/3/14.yaml --pixel1 4333 2901 --pixel2 3157 3375 --ned_origin_lat 39.578535 --ned_origin_lon 2.3502617 --crs EPSG:25831


"""



def georeference_png_to_geotiff(mosaic_path, out_path, pixel1, map1, pixel2, map2, crs="EPSG:25831"):
    row1, col1 = pixel1
    y1, x1 = map1
    row2, col2 = pixel2
    y2, x2 = map2

    img = Image.open(mosaic_path)
    arr = np.array(img)

    pixel_width = (x2 - x1) / (col2 - col1)
    pixel_height = (y2 - y1) / (row2 - row1)

    x_origin = x1 - (col1 + 0.5) * pixel_width
    y_origin = y1 - (row1 + 0.5) * pixel_height

    transform = from_origin(x_origin, y_origin, pixel_width, -pixel_height)

    if arr.ndim == 2:
        count = 1
    else:
        arr = np.transpose(arr, (2, 0, 1))
        count = arr.shape[0]

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
        if count == 1:
            dst.write(arr, 1)
        else:
            dst.write(arr)

    print(f"GeoTIFF written to {out_path}")

def get_world_from_hm_yaml_utm(yaml_path, ned_origin_lat, ned_origin_lon):
    """
    Reads a YAML HM, converts camera position from NED meters to UTM EPSG:25831.
    """
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    hm = np.array(data['HM']['data']).reshape((3,3))
    x_cam = hm[0,2]
    y_cam = hm[1,2]

    # Convert NED → lat/lon
    ned = NED(ned_origin_lat, ned_origin_lon, 0.0)
    lat, lon, _ = ned.ned2geodetic([x_cam, y_cam, 0.0])

    # Convert lat/lon → UTM 31N
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:25831", always_xy=True)
    easting, northing = transformer.transform(lon, lat)

    return northing, easting  # rasterio expects (Y, X)

def main():
    parser = argparse.ArgumentParser(description="Georeference a PNG using two HM YAMLs")
    parser.add_argument("--mosaic_path")
    parser.add_argument("--out_path")
    parser.add_argument("--yaml1", required=True)
    parser.add_argument("--yaml2", required=True)
    parser.add_argument("--pixel1", nargs=2, type=int, required=True)
    parser.add_argument("--pixel2", nargs=2, type=int, required=True)
    parser.add_argument("--ned_origin_lat", type=float, required=True)
    parser.add_argument("--ned_origin_lon", type=float, required=True)
    parser.add_argument("--crs", default="EPSG:25831")
    args = parser.parse_args()

    map1 = get_world_from_hm_yaml_utm(args.yaml1, args.ned_origin_lat, args.ned_origin_lon)
    map2 = get_world_from_hm_yaml_utm(args.yaml2, args.ned_origin_lat, args.ned_origin_lon)

    pixel1 = tuple(args.pixel1)
    pixel2 = tuple(args.pixel2)

    georeference_png_to_geotiff(
        args.mosaic_path,
        args.out_path,
        pixel1, map1,
        pixel2, map2,
        crs=args.crs
    )

if __name__ == "__main__":
    main()
