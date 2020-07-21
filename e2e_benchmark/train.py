import tensorflow as tf
from pathlib import Path

from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.model import unet


def train_model(data_path: Path, output_path: Path):
    batch_size = 32
    train_data_loader = SLSTRDataLoader(data_path, batch_size=batch_size)

    model = unet(train_data_loader.input_size)

    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    dataset = train_data_loader.to_dataset()
    model.fit(dataset, epochs=2)

    model_file = output_path / 'model.h5'
    model.save(model_file)
