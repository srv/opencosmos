import argparse
import os
from PIL import Image

# Disable pixel limit warning for large images
Image.MAX_IMAGE_PIXELS = None


def rotate_image(path):
    """Rotate a single image 90° counterclockwise and save as _rotated."""
    base, ext = os.path.splitext(path)
    if base.endswith("_rotated"):
        # Skip already rotated images
        return

    output_path = f"{base}_rotated{ext}"

    try:
        img = Image.open(path)
        rotated = img.rotate(90, expand=True)
        rotated.save(output_path)
        print(f"✅ Saved: {output_path}")
    except Exception as e:
        print(f"❌ Failed to process {path}: {e}")


def process_folder_recursively(root_folder):
    """Recursively process all PNGs in all subfolders."""
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith(".png"):
                image_path = os.path.join(dirpath, filename)
                rotate_image(image_path)


def main():
    parser = argparse.ArgumentParser(
        description="Recursively rotate all PNG images in a folder 90° counterclockwise."
    )
    parser.add_argument("--folder", required=True, help="Path to the folder to process.")
    args = parser.parse_args()

    process_folder_recursively(args.folder)
    print("🎯 Done.")


if __name__ == "__main__":
    main()

