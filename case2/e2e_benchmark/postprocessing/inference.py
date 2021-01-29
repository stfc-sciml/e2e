import h5py
import yaml
from pathlib import Path
import numpy as np
import tensorflow as tf
import horovod.tensorflow as hvd

from e2e_benchmark.monitor.logger import MultiLevelLogger
from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.constants import PATCH_SIZE, N_CHANNELS, IMAGE_H, IMAGE_W


def reconstruct_from_patches(patches, nx, ny, patch_size: int = PATCH_SIZE):
    h = ny * patch_size
    w = nx * patch_size
    reconstructed = np.zeros((1, h, w, 1))

    for i in range(ny):
        for j in range(nx):
            py = i * patch_size
            px = j * patch_size
            reconstructed[0, py:py + patch_size, px:px + patch_size] = patches[0, i, j]

    # Crop off the additional padding
    offset_y = (h - IMAGE_H) // 2
    offset_x = (w - IMAGE_W) // 2
    reconstructed = tf.image.crop_to_bounding_box(reconstructed, offset_y, offset_x, IMAGE_H, IMAGE_W)

    return reconstructed


def main(model_file: Path, data_dir: Path, output_dir: Path, user_argv: dict):
    hvd.init()

    # Pin the number of GPUs to the local rank for Horovod
    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    if gpus:
        tf.config.experimental.set_visible_devices(
            gpus[hvd.local_rank()], 'GPU')

    CROP_SIZE = user_argv['crop_size']

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger = MultiLevelLogger(output_dir / 'inference_logs.txt')

    # If not model provided, try to load it from the output folder
    if model_file is None:
        model_file = Path(output_dir / 'model.h5')

    logger.message('Loading model {}'.format(model_file))
    assert Path(model_file).exists(), "Model file does not exist!"
    model = tf.keras.models.load_model(str(model_file))

    logger.message('Getting file paths')
    file_paths = list(Path(data_dir).glob('**/S3A*.hdf'))
    assert len(file_paths) > 0, "Could not find any HDF files!"

    logger.message('Preparing data loader')
    # Create data loader in single image mode. This turns off shuffling and
    # only yields batches of images for a single image at a time so they can be
    # reconstructed.
    data_loader = SLSTRDataLoader(file_paths, single_image=True, crop_size=CROP_SIZE)
    dataset = data_loader.to_dataset()

    user_argv['num_gpus'] = len(gpus)
    user_argv['num_ranks'] = hvd.size()

    if hvd.rank() == 0:
        logger.message(f"Num GPUS: {len(gpus)}")
        logger.message(f"Num ranks: {hvd.size()}")
        logger.begin('Inference Loop')

    for patches, file_name in dataset:
        file_name = Path(file_name.numpy().decode('utf-8'))
        logger.message(f"Processing file {file_name}")

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

    if hvd.rank() == 0:
        logger.ended('Inference Loop')

        # Save parameters
        with (output_dir / 'inference_params.yml').open('w') as handle:
            yaml.dump(user_argv, handle)

