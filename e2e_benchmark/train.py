import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from pathlib import Path

from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.model import unet


def weighted_cross_entropy(beta):
    def convert_to_logits(y_pred):
        # see https://github.com/tensorflow/tensorflow/blob/r1.10/tensorflow/python/keras/backend.py#L3525
        y_pred = tf.clip_by_value(y_pred, tf.keras.backend.epsilon(), 1 - tf.keras.backend.epsilon())

        return tf.math.log(y_pred / (1 - y_pred))

    def loss(y_true, y_pred):
        y_pred = convert_to_logits(y_pred)
        loss = tf.nn.weighted_cross_entropy_with_logits(logits=y_pred, labels=y_true, pos_weight=beta)

        # or reduce_sum and/or axis=-1
        return tf.reduce_mean(loss)

    return loss


def save_images(path: str, images: np.ndarray, masks: np.ndarray, predicted: np.ndarray):
    fig, axes = plt.subplots(5, 4, figsize=(10, 10))

    for i, row in enumerate(axes):
        ax1, ax2, ax3, ax4 = row
        ax1.matshow(images[i, ..., 7])
        ax2.matshow(masks[i, ..., 0], vmin=0, vmax=1)
        ax3.matshow(predicted[i, ..., 0], vmin=0, vmax=1)
        ax4.matshow(predicted[i, ..., 0] > .5, vmin=0, vmax=1)

        for ax in row:
            ax.axis('off')

    plt.savefig(path)
    plt.close()


def train_model(data_path: Path, output_path: Path):
    batch_size = 32
    train_data_loader = SLSTRDataLoader(data_path, batch_size=batch_size)

    model = unet(train_data_loader.input_size)

    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    bce = weighted_cross_entropy(.5)
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    dataset = train_data_loader.to_dataset()

    loss_metric = tf.keras.metrics.Mean()
    acc_metric = tf.keras.metrics.BinaryAccuracy()

    @tf.function
    def train_step(images, masks):
        with tf.GradientTape() as tape:
            predicted = model(images)
            clip_offset = 15
            predicted = predicted[:, clip_offset:-clip_offset, clip_offset:-clip_offset]
            masks = masks[:, clip_offset:-clip_offset, clip_offset:-clip_offset]
            loss = bce(masks, predicted)
            loss_metric.update_state(loss)

        gradients = tape.gradient(
            loss, model.trainable_variables)

        optimizer.apply_gradients(
            zip(gradients, model.trainable_variables))

        return predicted, masks

    epochs = 30
    for epoch in range(epochs):
        # Clear epoch metrics
        loss_metric.reset_states()
        acc_metric.reset_states()

        # Train model
        for i, (images, masks) in enumerate(dataset):
            predicted, msk = train_step(images, masks)
            acc_metric.update_state(msk, predicted)
            print('Batch: {}, Accuracy: {}'.format(i, acc_metric.result().numpy()))

            if i % 10:
                save_images(output_path / 'epoch_{}_{}.png'.format(epoch, i), images.numpy(), masks.numpy(), predicted.numpy())

        # Print metrics
        loss_value = loss_metric.result().numpy()

        print('Epoch {}, Loss: {}'.format(epoch, loss_value))
        model_file = output_path / 'model.h5'
        model.save(model_file)
