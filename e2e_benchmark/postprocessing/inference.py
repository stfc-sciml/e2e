import h5py
from pathlib import Path
from tqdm import tqdm
import numpy as np
import tensorflow as tf

from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.constants import PATCH_SIZE, N_CHANNELS, IMAGE_H, IMAGE_W


def reconstruct_from_patches(patches, nx, ny, patch_size: int = PATCH_SIZE):
    # n, nx, ny, _, _, c = patches.shape

    h = ny * patch_size
    w = nx * patch_size
    out = np.zeros((1, h, w, 1))

    for i in range(ny):
        for j in range(nx):
            py = i * patch_size
            px = j * patch_size
            out[0, py:py + patch_size, px:px + patch_size] = patches[0, i, j]

    # Crop off the additional padding
    offset_y = (h - IMAGE_H) // 2
    offset_x = (w - IMAGE_W) // 2
    out = tf.image.crop_to_bounding_box(out, offset_y, offset_x, IMAGE_H, IMAGE_W)

    return out


def main(model_file, data_dir, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model = tf.keras.models.load_model(model_file)

    file_paths = list(Path(data_dir).glob('**/S3A*.hdf'))

    # Create data loader in single image mode. This turns off shuffling and
    # only yields batches of images for a single image at a time so they can be
    # reconstructed.
    CROP_SIZE = 80
    data_loader = SLSTRDataLoader(file_paths, single_image=True, crop_size=CROP_SIZE)
    dataset = data_loader.to_dataset()

    for file_name, (patches, _) in tqdm(zip(file_paths, dataset), total=len(file_paths)):
        # convert patches to a batch of patches
        n, ny, nx, np = patches.shape
        patches = tf.reshape(patches, (n * nx * ny, PATCH_SIZE, PATCH_SIZE, N_CHANNELS))

        # perform inference on patches
        mask_patches = model.predict_on_batch(patches)

        # crop edge artifacts
        mask_patches = tf.image.crop_to_bounding_box(mask_patches, CROP_SIZE // 2, CROP_SIZE // 2, PATCH_SIZE - CROP_SIZE, PATCH_SIZE - CROP_SIZE)

        # reconstruct patches back to full size image
        mask_patches = tf.reshape(mask_patches, (n, ny, nx, PATCH_SIZE - CROP_SIZE, PATCH_SIZE - CROP_SIZE, 1))
        mask = reconstruct_from_patches(mask_patches, nx, ny, patch_size=PATCH_SIZE - CROP_SIZE)
        mask_name = (output_dir / file_name.name).with_suffix('.h5')

        with h5py.File(mask_name, 'w') as handle:
            handle.create_dataset('mask', data=mask)
