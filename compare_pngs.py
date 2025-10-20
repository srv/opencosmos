import argparse
import os
from PIL import Image

# Disable Pillow safety limits for large images
Image.MAX_IMAGE_PIXELS = None


def compare_and_filter_all(images, filenames):
    """Apply the transparency/black pixel filter across all images."""
    width, height = images[0].size
    pixel_data = [img.load() for img in images]

    for y in range(height):
        for x in range(width):
            make_transparent = False

            # Check each image’s pixel
            for idx, pixels in enumerate(pixel_data):
                r, g, b, a = pixels[x, y]

                # Transparent or black (if mosaic_x)
                if a == 0 or ("mosaic_x" in filenames[idx].lower() and (r, g, b) == (0, 0, 0)):
                    make_transparent = True
                    break

            # Apply transparency to all
            if make_transparent:
                for p in pixel_data:
                    p[x, y] = (0, 0, 0, 0)

    return images


def compare_all_pngs_in_folder(folder_path):
    """Process one folder containing PNGs."""
    png_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(".png")
    ]

    if len(png_files) < 2:
        return  # Not enough images to compare

    print(f"\nProcessing folder: {folder_path}")

    # Load images in RGBA
    all_images = [(p, Image.open(p).convert("RGBA")) for p in png_files]

    # Determine reference size from the first non-mosaic_over image
    ref_image = next((img for path, img in all_images if "mosaic_over" not in path.lower()), None)
    if not ref_image:
        print(f"⚠️  No base image found in {folder_path} (only 'mosaic_over' files). Skipping.")
        return

    ref_size = ref_image.size

    # Filter images: skip mosaic_over with different size
    filtered = []
    for path, img in all_images:
        if img.size != ref_size:
            if "mosaic_over" in path.lower():
                print(f"⚠️  Skipping '{os.path.basename(path)}' (size {img.size} != {ref_size})")
                continue
            else:
                raise ValueError(
                    f"❌ Images in {folder_path} must have the same dimensions. "
                    f"Found mismatch: {os.path.basename(path)} is {img.size}, expected {ref_size}"
                )
        filtered.append((path, img))

    if len(filtered) < 2:
        print(f"⚠️  Not enough valid images to compare in {folder_path}. Skipping.")
        return

    # Apply filtering
    filenames = [p for p, _ in filtered]
    images = [img for _, img in filtered]
    images = compare_and_filter_all(images, filenames)

    # Save back
    for path, img in zip(filenames, images):
        img.save(path, "PNG")

    print(f"✅ Updated {len(filenames)} images in {folder_path}")


def process_folder_recursively(root_folder):
    """Scan all subfolders for PNGs."""
    for dirpath, _, filenames in os.walk(root_folder):
        if any(f.lower().endswith(".png") for f in filenames):
            compare_all_pngs_in_folder(dirpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Recursively compare all PNGs in each folder, removing pixels transparent in any image.\n"
            "- In 'mosaic_x' files, black pixels are also treated as transparent.\n"
            "- 'mosaic_over' images with different sizes are skipped (warning only)."
        )
    )
    parser.add_argument("--folder", required=True, help="Root folder to scan recursively.")
    args = parser.parse_args()

    process_folder_recursively(args.folder)

