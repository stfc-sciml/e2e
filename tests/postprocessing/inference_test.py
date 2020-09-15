import numpy as np
import tensorflow as tf
from e2e_benchmark.constants import PATCH_SIZE, IMAGE_H, IMAGE_W
from e2e_benchmark.postprocessing.inference import reconstruct_from_patches


def test_reconstruct_from_patches():
    img_shape = (1, IMAGE_H, IMAGE_W, 1)
    img = np.random.random(img_shape)

    # Convert image to a batch of patches
    dims = [1, PATCH_SIZE, PATCH_SIZE, 1]
    patches = tf.image.extract_patches(img, dims, dims, [1, 1, 1, 1], padding='SAME')
    n, ny, nx, _ = patches.shape
    batch = tf.reshape(patches, (n * nx * ny, PATCH_SIZE, PATCH_SIZE, 1))
    batch = tf.reshape(batch, (n, ny, nx, PATCH_SIZE, PATCH_SIZE, 1))

    # Reconstuct batch back to full image size
    recon_img = reconstruct_from_patches(batch.numpy(), nx, ny)

    assert recon_img.shape == img_shape
    assert np.all(np.absolute(recon_img - img) < 1e-6)


def test_reconstruct_from_patches_cropped():
    CROP_SIZE = 20
    img_shape = (1, IMAGE_H, IMAGE_W, 1)
    img = np.random.random(img_shape)

    # Convert image to a batch of patches
    dims = [1, PATCH_SIZE, PATCH_SIZE, 1]
    strides = [1, PATCH_SIZE - CROP_SIZE, PATCH_SIZE - CROP_SIZE, 1]
    patches = tf.image.extract_patches(img, dims, strides, [1, 1, 1, 1], padding='SAME')
    n, ny, nx, _ = patches.shape
    batch = tf.reshape(patches, (n * nx * ny, PATCH_SIZE, PATCH_SIZE, 1))
    batch = tf.image.crop_to_bounding_box(batch, CROP_SIZE // 2, CROP_SIZE // 2, PATCH_SIZE - CROP_SIZE, PATCH_SIZE - CROP_SIZE)
    batch = tf.reshape(batch, (n, ny, nx, PATCH_SIZE - CROP_SIZE, PATCH_SIZE - CROP_SIZE, 1))

    # Reconstuct batch back to full image size
    recon_img = reconstruct_from_patches(batch.numpy(), nx, ny, PATCH_SIZE - CROP_SIZE)

    assert recon_img.shape == img_shape
    assert np.all(np.absolute(recon_img - img) < 1e-6)
