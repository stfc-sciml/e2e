from pathlib import Path

import h5py
import tensorflow as tf
import numpy as np

from e2e_benchmark.constants import PATCH_SIZE, IMAGE_H, IMAGE_W
from typing import Union, List

N_CHANNELS = 9


class SLSTRDataLoader:

    def __init__(self, paths: Union[Path, List[Path]], shuffle: bool = True, batch_size: int = 32, single_image: bool = False):
        if paths.is_dir():
            self._image_paths = Path(self._data_dir).glob('**/S3A*.hdf')
        else:
            self._image_paths = paths

        self._image_paths = list(map(str, self._image_paths))

        self._shuffle = shuffle
        self.batch_size = batch_size

        self.single_image = single_image
        self.patch_padding = 'valid' if not single_image else 'same'

        assert len(self._image_paths) > 0, 'No image data found in path!'

    @property
    def input_size(self):
        return (PATCH_SIZE, PATCH_SIZE, N_CHANNELS)

    @property
    def output_size(self):
        return (PATCH_SIZE, PATCH_SIZE, 1)

    def _load_data(self, path):
        path = path.decode()

        with h5py.File(path, 'r') as handle:
            refs = handle['refs'][:]
            bts = handle['bts'][:]
            msk = handle['bayes'][:]

        bts = (bts - 270.0) / 22.0
        refs = refs - 0.5
        img = np.concatenate([refs, bts], axis=-1)

        msk[msk > 0] = 1
        msk[msk == 0] = 0
        msk = msk.astype(np.float)

        yield img, msk

    def _preprocess_images(self, img, msk):
        # Crop & convert to patches
        img = self._transform_image(img)
        msk = self._transform_image(msk)

        return img, msk

    def _transform_image(self, img):
        # Crop to image which is divisible by the patch size
        # This also removes boarders of image which are all zero
        offset_h = (IMAGE_H % PATCH_SIZE) // 2
        offset_w = (IMAGE_W % PATCH_SIZE) // 2

        target_h = IMAGE_H - offset_h * 2
        target_w = IMAGE_W - offset_w * 2

        img = tf.image.crop_to_bounding_box(img, offset_h, offset_w, target_h, target_w)

        # Covert image from IMAGE_H x IMAGE_W to PATCH_SIZE x PATCH_SIZE
        dims = [1, PATCH_SIZE, PATCH_SIZE, 1]
        img = tf.expand_dims(img, axis=0)
        b, h, w, c = img.shape
        img = tf.image.extract_patches(img, dims, dims, [1, 1, 1, 1], padding=self.patch_padding.upper())

        if not self.single_image:
            n, nx, ny, np = img.shape
            img = tf.reshape(img, (n * nx * ny, PATCH_SIZE, PATCH_SIZE, c))

        return img

    def _generator(self, path):
        types = (tf.float32, tf.float32)
        shapes = (tf.TensorShape([IMAGE_H, IMAGE_W, N_CHANNELS]),
                  tf.TensorShape([IMAGE_H, IMAGE_W, 1]))
        dataset = tf.data.Dataset.from_generator(self._load_data,
                                                 output_types=types,
                                                 output_shapes=shapes,
                                                 args=(path, ))
        return dataset

    def to_dataset(self):
        """Input function for training"""
        dataset = tf.data.Dataset.from_tensor_slices(self._image_paths)

        if self._shuffle:
            dataset = dataset.shuffle(len(self._image_paths))

        dataset = dataset.interleave(self._generator, cycle_length=8, num_parallel_calls=8)
        dataset = dataset.map(self._preprocess_images, num_parallel_calls=8)

        if self.single_image:
            return dataset

        dataset = dataset.unbatch()
        dataset = dataset.cache()
        dataset = dataset.prefetch(self.batch_size * 3)

        if self._shuffle:
            dataset = dataset.shuffle(self.batch_size * 3)

        dataset = dataset.batch(self.batch_size)
        return dataset
