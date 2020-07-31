import pytest
import numpy as np
from pathlib import Path

from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.constants import PATCH_SIZE, IMAGE_H, IMAGE_W


@pytest.fixture()
def data_dir():
    path = Path("data/processed/pixbox")
    assert path.exists()
    return path


def test_sentinel3_dataset(data_dir):
    batch_size = 2
    dataset = SLSTRDataLoader(data_dir, batch_size=batch_size).to_dataset()
    batch = next(dataset.as_numpy_iterator())
    img, msk = batch

    # Image shape
    b, h, w, c = img.shape

    assert b == batch_size
    assert h == PATCH_SIZE
    assert w == PATCH_SIZE
    assert c == 9
    assert np.count_nonzero(img[0]) > 0
    assert np.all(np.isfinite(img[..., 6:]))
    assert np.all(np.isfinite(img[..., :6]))

    # Mask shape
    b, h, w, c = msk.shape

    assert b == batch_size
    assert h == PATCH_SIZE
    assert w == PATCH_SIZE
    assert c == 1
    assert np.count_nonzero(msk[0]) > 0
    assert np.all(np.isfinite(msk))
    assert msk.max() == 1
    assert msk.min() == 0


def test_sentinel3_dataset_single_image_mode(data_dir):
    dataset = SLSTRDataLoader(data_dir, single_image=True).to_dataset()
    batch = next(dataset.as_numpy_iterator())
    img, msk = batch

    # Image shape
    n, ny, nx, pixels = img.shape

    assert n == 1
    assert ny == np.ceil(IMAGE_H / PATCH_SIZE)
    assert nx == np.ceil(IMAGE_W / PATCH_SIZE)
