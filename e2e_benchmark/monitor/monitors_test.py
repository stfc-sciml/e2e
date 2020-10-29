import pickle
import time
import numpy as np
import tensorflow as tf
from e2e_benchmark.monitor.monitors import RuntimeMonitor, SystemMonitor


def load_logs(path):
    with open(path, 'rb') as handle:
        while True:
            try:
                yield pickle.load(handle)
            except EOFError:
                break


def test_runtime_monitor_report(tmp_path):
    report_file = tmp_path / 'report.pkl'

    monitor = RuntimeMonitor(report_file)
    monitor.start()
    items = [('int', 10),
             ('float', 10.0),
             ('string', "hello world"),
             ('numpy', np.ones((10, 10))),
             ('tf_tensor', tf.constant([1, 2, 3])),
             ('dict', dict(an_int=int, a_float=1.0, a_list=[1, 2, 3])),
             ('list', [1, 4.0, 'hello'])]

    for key, value in items:
        monitor.report(key, value)

    monitor.stop()

    for (expected_name, expected_value), log in zip(items, load_logs(report_file)):
        assert log['name'] == expected_name
        if expected_name == 'numpy' or expected_name == 'tf_tensor':
            assert np.all(log['value'] == expected_value)
        else:
            assert log['value'] == expected_value


def test_system_monitor(tmp_path):
    report_file = tmp_path / 'sys_logs.pkl'

    monitor = SystemMonitor(report_file, interval=0.1)
    monitor.start()
    time.sleep(1)
    monitor.stop()

    logs = list(load_logs(report_file))

    assert len(logs) > 0

    for log in logs:
        assert log['name'] == 'system_info' or log['name'] == 'system_state'


def test_system_monitor(tmp_path):
    report_file = tmp_path / 'sys_log.pkl'
    monitor = RuntimeMonitor(tmp_path)
    sys_mon = monitor.system_monitor(report_file, 0.1)
    sys_mon.start()
    time.sleep(1)
    sys_mon.stop()

    assert report_file.exists()
