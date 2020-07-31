import click
from pathlib import Path
import numpy as np
import tensorflow as tf

from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.constants import PATCH_SIZE, IMAGE_H, IMAGE_W


def reconstruct_from_patches(patches):
    out = np.zeros((1, 600, 600, 3))
    for i, patch in enumerate(patches.numpy()):
        px = (i % nx) * PATCH_SIZE
        py = (i // ny) * PATCH_SIZE
        out[0, py:py + PATCH_SIZE, px:px + PATCH_SIZE] = patch


@click.command()
@click.argument('model-file')
@click.argument('sst-file')
@click.argument('data-dir')
def main(model_file, sst_file, data_dir):

    model = tf.keras.models.load_model(model_file)

    file_paths = Path(data_dir).glob('**/S3A*.hdf')

    # Create data loader in single image mode. This turns off shuffling and
    # only yields batches of images for a single image at a time so they can be
    # reconstructed.
    data_loader = SLSTRDataLoader(file_paths, single_image=True)
    dataset = data_loader.to_dataset()

    for file_name, (patches, _) in zip(file_paths, dataset):
        mask_patches = model.predicton_batch(patches)
        print(mask_patches.shape)



if __name__ == "__main__":
    main()
