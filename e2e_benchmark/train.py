from os.path import split

import tensorflow as tf
import horovod.tensorflow as hvd
from pathlib import Path

from sklearn.model_selection import train_test_split

from e2e_benchmark.monitor.logger import MultiLevelLogger
from e2e_benchmark.monitor.monitors import RuntimeMonitor
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
    logger = MultiLevelLogger(output_path / 'training_log.txt')
    hvd.init()

    learning_rate = user_argv['learning_rate']
    epochs = user_argv['epochs']
    batch_size = user_argv['batch_size']
    wbce = user_argv['wbce']
    clip_offset = user_argv['clip_offset']

    # Pin the number of GPUs to the local rank for Horovod
    gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    if gpus:
        tf.config.experimental.set_visible_devices(
            gpus[hvd.local_rank()], 'GPU')

    # Setup runtime monitoring to track metrics, parameters & system usage
    monitor = RuntimeMonitor(path=output_path / 'train_log.pkl')
    monitor.start()

    if hvd.rank() == 0:
        logger.message(f"Num GPUS: {len(gpus)}")
        logger.message(f"Num ranks: {hvd.size()}")
        monitor.report('user_args', user_argv)

    # Get the data loader
    data_paths = list(Path(data_path).glob('**/S3A*.hdf'))
    train_paths, test_paths = train_test_split(data_paths, train_size=user_argv['train_split'], random_state=42)

    train_data_loader = SLSTRDataLoader(train_paths, batch_size=batch_size)
    train_dataset = train_data_loader.to_dataset()

    test_data_loader = SLSTRDataLoader(test_paths, batch_size=batch_size)
    test_dataset = test_data_loader.to_dataset()

    model = unet(train_data_loader.input_size)

    # Setup the loss functions and optimizer
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    bce = weighted_cross_entropy(wbce)
    model.compile(optimizer=optimizer,
                  loss='binary_crossentropy', metrics=['accuracy'])

    train_loss_metric = tf.keras.metrics.Mean()
    train_acc_metric = tf.keras.metrics.BinaryAccuracy()

    test_loss_metric = tf.keras.metrics.Mean()
    test_acc_metric = tf.keras.metrics.BinaryAccuracy()

    if hvd.rank() == 0: logger.begin("Training Loop")

    @tf.function
    def train_step(images, masks, first_batch=False):
        with tf.GradientTape() as tape:
            predicted = model(images)
            predicted = predicted[:, clip_offset:-
                                  clip_offset, clip_offset:-clip_offset]
            masks = masks[:, clip_offset:-
                          clip_offset, clip_offset:-clip_offset]
            loss = bce(masks, predicted)
            train_loss_metric.update_state(loss)

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

    @tf.function
    def test_step(images, masks, first_batch=False):
        predicted = model(images)
        predicted = predicted[:, clip_offset:-
        clip_offset, clip_offset:-clip_offset]
        masks = masks[:, clip_offset:-
        clip_offset, clip_offset:-clip_offset]
        loss = bce(masks, predicted)
        test_loss_metric.update_state(loss)
        return predicted, masks

    # Start monitoring of device resources for each node
    if gpus:
        device_log_file = output_path / f'device_{hvd.rank()}.pkl'
        dev_monitor = monitor.device_monitor(device_log_file, index=hvd.rank(), interval=1)
        dev_monitor.start()

    # Start monitoring wall time of training
    if hvd.rank() == 0: monitor.start_timer(name='training_time')

    # Start monitoring system resources for each node
    sys_log_file = output_path / f'train_rank_{hvd.rank()}.pkl'
    sys_monitor = monitor.system_monitor(sys_log_file, interval=1)
    sys_monitor.start()

    for epoch in range(epochs):
        # Clear epoch metrics
        train_loss_metric.reset_states()
        train_acc_metric.reset_states()

        test_loss_metric.reset_states()
        test_acc_metric.reset_states()

        if hvd.rank() == 0:
            logger.begin(f"Epoch {epoch}")
            logger.begin("Training")
            monitor.start_timer(name=f'epoch_{epoch}_time')

        # Train model
        for i, (images, masks) in enumerate(train_dataset):
            predicted, msk = train_step(images, masks, i == 0)
            train_acc_metric.update_state(msk, predicted)
            if hvd.rank() == 0:
                message = f'Batch: {i}, Train Loss: {train_loss_metric.result().numpy(): .5f}'
                logger.message(message)

        if hvd.rank() == 0:
            logger.ended("Training")
            logger.begin("Testing")

        # Test model
        for i, (images, masks) in enumerate(test_dataset):
            predicted, msk = test_step(images, masks, i == 0)
            test_acc_metric.update_state(msk, predicted)
            if hvd.rank() == 0:
                message = f'Batch: {i}, Test Loss: {test_loss_metric.result().numpy(): .5f}'
                logger.message(message)

        # Log Epoch Results
        if hvd.rank() == 0:
            monitor.stop_timer(name=f'epoch_{epoch}_time')
            logger.ended('Testing')
            logger.ended("Epoch")

            # Print metrics
            train_loss = train_loss_metric.result().numpy()
            train_accuracy = train_acc_metric.result().numpy()

            test_loss = test_loss_metric.result().numpy()
            test_accuracy = test_acc_metric.result().numpy()

            message = f'Epoch {epoch}, Train Loss: {train_loss:.5f}, Test Loss: {test_loss:.5f}, Train Acc: {train_accuracy: .2f}, Test Acc: {test_accuracy: .2f}'
            logger.message(message)

            # Save model
            model_file = output_path / 'model.h5'
            model.save(model_file)

            monitor.report(f'epoch_{epoch}', dict(train_accuracy=train_accuracy, epoch=epoch, train_loss=train_loss,
                                                  test_accuracy=test_accuracy, test_loss=test_loss))

    # Stop monitors
    if hvd.rank() == 0:
        logger.ended("Training Loop")
        monitor.stop_timer(name='training_time')

    sys_monitor.stop()

    if gpus:
        dev_monitor.stop()

    monitor.stop()
