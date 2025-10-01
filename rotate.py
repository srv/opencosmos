import argparse
import os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

def main():
    parser = argparse.ArgumentParser(description="Rotate a PNG image 90° counterclockwise.")
    parser.add_argument("--input", required=True, help="Path to the input PNG image")
    args = parser.parse_args()

    # Open image
    img = Image.open(args.input)

    # Rotate 90 degrees counterclockwise
    rotated = img.rotate(90, expand=True)

    # Build output path: same folder, add _rotated before extension
    base, ext = os.path.splitext(args.input)
    output_path = f"{base}_rotated{ext}"

    # Save result
    rotated.save(output_path)
    print(f"Rotated image saved as: {output_path}")

if __name__ == "__main__":
    main()