import h5py
import click
from pathlib import Path
from tqdm import tqdm
import numpy as np
import tensorflow as tf

from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.constants import PATCH_SIZE, N_CHANNELS, IMAGE_H, IMAGE_W


def reconstruct_from_patches(patches, nx, ny):
    # n, nx, ny, _, _, c = patches.shape

    h = ny * PATCH_SIZE
    w = nx * PATCH_SIZE
    out = np.zeros((1, h, w, 1))

    for i in range(ny):
        for j in range(nx):
            py = i * PATCH_SIZE
            px = j * PATCH_SIZE
            out[0, py:py + PATCH_SIZE, px:px + PATCH_SIZE] = patches[0, i, j]

    # Crop off the additional padding
    offset_y = (h - IMAGE_H) // 2
    offset_x = (w - IMAGE_W) // 2
    out = tf.image.crop_to_bounding_box(out, offset_y, offset_x, IMAGE_H, IMAGE_W)

    return out


@click.command()
@click.argument('model-file')
@click.argument('data-dir')
@click.argument('output-dir')
def main(model_file, data_dir, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = tf.keras.models.load_model(model_file)

    file_paths = list(Path(data_dir).glob('**/S3A*.hdf'))

    # Create data loader in single image mode. This turns off shuffling and
    # only yields batches of images for a single image at a time so they can be
    # reconstructed.
    data_loader = SLSTRDataLoader(file_paths, single_image=True)
    dataset = data_loader.to_dataset()

    for file_name, (patches, _) in tqdm(zip(file_paths, dataset), total=len(file_paths)):
        # convert patches to a batch of patches
        n, ny, nx, np = patches.shape
        patches = tf.reshape(patches, (n * nx * ny, PATCH_SIZE, PATCH_SIZE, N_CHANNELS))

        # perform inference on patches
        mask_patches = model.predict_on_batch(patches)

        # reconstruct patches back to full size image
        mask_patches = tf.reshape(mask_patches, (n, ny, nx, PATCH_SIZE, PATCH_SIZE, 1))
        mask = reconstruct_from_patches(mask_patches, nx, ny)
        mask_name = (output_dir / file_name.name).with_suffix('.h5')

        with h5py.File(mask_name, 'w') as handle:
            handle.create_dataset('mask', data=mask)


if __name__ == "__main__":
    main()
