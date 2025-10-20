import argparse
import os
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

def main():
    parser = argparse.ArgumentParser(description="Make black pixels transparent in a PNG image.")
    parser.add_argument("--input", required=True, help="Path to the input PNG image")
    args = parser.parse_args()

    # Open image and ensure RGBA mode
    img = Image.open(args.input).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # item is (R, G, B, A)
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            # Make black pixels transparent
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)

    # Apply new data
    img.putdata(new_data)

    # Build output path
    base, ext = os.path.splitext(args.input)
    output_path = f"{base}_transparent{ext}"

    # Save as PNG with alpha
    img.save(output_path, "PNG")
    print(f"Image with transparent black pixels saved as: {output_path}")

if __name__ == "__main__":
    main()

