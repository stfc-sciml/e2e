import h5py
from pathlib import Path
from tqdm import tqdm
import numpy as np
import tensorflow as tf

from e2e_benchmark.monitor.logger import MultiLevelLogger
from e2e_benchmark.monitor.monitors import RuntimeMonitor
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
    CROP_SIZE = user_argv['crops_size']
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger = MultiLevelLogger(output_dir / 'inference_logs.txt')

    monitor = RuntimeMonitor(output_dir / 'inference_logs.pkl')
    monitor.start()
    monitor.report('user_args', user_argv)

    model = tf.keras.models.load_model(model_file)
    file_paths = list(Path(data_dir).glob('**/S3A*.hdf'))

    # Create data loader in single image mode. This turns off shuffling and
    # only yields batches of images for a single image at a time so they can be
    # reconstructed.
    data_loader = SLSTRDataLoader(file_paths, single_image=True, crop_size=CROP_SIZE)
    dataset = data_loader.to_dataset()

    # Start system and  device monitor
    sys_monitor = monitor.system_monitor(output_dir / 'inference_system_logs.pkl', interval=1)
    device_monitor = monitor.device_monitor(output_dir / 'inference_device_logs.pkl', interval=1)

    sys_monitor.start()
    device_monitor.start()
    monitor.start_timer(name='inference_time')

    logger.begin('Inference Loop')
    for file_name, (patches, _) in tqdm(zip(file_paths, dataset), total=len(file_paths)):
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

    logger.ended('Inference Loop')

    monitor.end_timer(name='inference_time')
    sys_monitor.end()
    device_monitor.end()
    monitor.end()