import tensorflow as tf
import horovod.tensorflow as hvd
from pathlib import Path

from e2e_benchmark.data_loader import SLSTRDataLoader
from e2e_benchmark.model import unet


def weighted_cross_entropy(beta):
    def convert_to_logits(y_pred):
        # see https://github.com/tensorflow/tensorflow/blob/r1.10/tensorflow/python/keras/backend.py#L3525
        y_pred = tf.clip_by_value(
            y_pred, tf.keras.backend.epsilon(), 1 - tf.keras.backend.epsilon())

        return tf.math.log(y_pred / (1 - y_pred))

    def loss(y_true, y_pred):
        y_pred = convert_to_logits(y_pred)
        loss = tf.nn.weighted_cross_entropy_with_logits(
            logits=y_pred, labels=y_true, pos_weight=beta)

        # or reduce_sum and/or axis=-1
        return tf.reduce_mean(loss)

    return loss


def train_model(data_path: Path, output_path: Path, user_argv: dict):
    learning_rate = user_argv['learning_rate']
    epochs = user_argv['epochs']
    batch_size = user_argv['batch_size']
    wbce = user_argv['wbce']
    clip_offset = user_argv['clip_offset']

    hvd.init()
    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    if gpus:
        tf.config.experimental.set_visible_devices(
            gpus[hvd.local_rank()], 'GPU')

    train_data_loader = SLSTRDataLoader(data_path, batch_size=batch_size)

    model = unet(train_data_loader.input_size)

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    bce = weighted_cross_entropy(wbce)
    model.compile(optimizer=optimizer,
                  loss='binary_crossentropy', metrics=['accuracy'])

    dataset = train_data_loader.to_dataset()

    loss_metric = tf.keras.metrics.Mean()
    acc_metric = tf.keras.metrics.BinaryAccuracy()

    @tf.function
    def train_step(images, masks, first_batch=False):
        with tf.GradientTape() as tape:
            predicted = model(images)
            predicted = predicted[:, clip_offset:-
                                  clip_offset, clip_offset:-clip_offset]
            masks = masks[:, clip_offset:-
                          clip_offset, clip_offset:-clip_offset]
            loss = bce(masks, predicted)
            loss_metric.update_state(loss)

        tape = hvd.DistributedGradientTape(tape)
        gradients = tape.gradient(
            loss, model.trainable_variables)

        optimizer.apply_gradients(
            zip(gradients, model.trainable_variables))

        # Horovod: broadcast initial variable states from rank 0 to all other processes.
        # This is necessary to ensure consistent initialization of all workers when
        # training is started with random weights or restored from a checkpoint.
        #
        # Note: broadcast should be done after the first gradient step to ensure optimizer
        # initialization.
        if first_batch:
            hvd.broadcast_variables(model.variables, root_rank=0)
            hvd.broadcast_variables(optimizer.variables(), root_rank=0)

        return predicted, masks

    for epoch in range(epochs):
        # Clear epoch metrics
        loss_metric.reset_states()
        acc_metric.reset_states()

        # Train model
        for i, (images, masks) in enumerate(dataset):
            predicted, msk = train_step(images, masks, i == 0)
            acc_metric.update_state(msk, predicted)
            if hvd.rank() == 0:
                print('Batch: {}, Accuracy: {}'.format(
                    i, acc_metric.result().numpy()))

        if hvd.rank() == 0:
            # Print metrics
            loss_value = loss_metric.result().numpy()
            print('Epoch {}, Loss: {}'.format(epoch, loss_value))
            model_file = output_path / 'model.h5'
            model.save(model_file)
