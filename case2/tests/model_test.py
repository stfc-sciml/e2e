import tensorflow as tf
import numpy as np
from e2e_benchmark.model import unet


def test_unet():
    model = unet((128, 128, 2))

    assert isinstance(model, tf.keras.Model)
    assert model.input_shape == (None, 128, 128, 2)
    assert model.output_shape == (None, 128, 128, 1)


def test_unet_feed_forward():
    X = np.random.random((1, 128, 128, 2))
    model = unet((128, 128, 2))
    output = model.predict(X)
    assert output.shape == (1, 128, 128, 1)


def test_unet_v1_backprop():
    X = np.random.random((1, 128, 128, 2))
    Y = np.random.randint(0, 1, size=(1, 128, 128, 1))
    model = unet((128, 128, 2))
    model.compile(loss='binary_crossentropy', optimizer='adam')
    history = model.fit(X, Y)
    assert isinstance(history, tf.keras.callbacks.History)
