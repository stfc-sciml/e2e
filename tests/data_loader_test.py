import tensorflow as tf
import pytest
import numpy as np
from pathlib import Path

from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.constants import PATCH_SIZE


@pytest.fixture()
def data_dir():
    path = Path("data/processed/pixbox")
    assert path.exists()
    return path


def test_sentinel3_dataset_train_fn(data_dir):
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
