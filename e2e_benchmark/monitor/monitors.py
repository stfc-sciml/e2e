from e2e_benchmark.monitor.system import HostSpec, DeviceSpec
from e2e_benchmark.monitor.logger import SimpleTimer
from datetime import datetime
from threading import Timer
from pathlib import Path
import pickle


class RuntimeMonitor:

    def __init__(self, path):
        self._path = path
        self._timers = {}

    def start(self):
        self._file_handle = open(self._path, 'wb+')

    def stop(self):
        self._file_handle.close()

    def report(self, name, value):
        timestamp = datetime.now()
        timestamp = timestamp.isoformat()
        payload = dict(name=name, value=value, timestamp=timestamp)
        pickle.dump(payload, self._file_handle)

    def start_timer(self, name):
        self._timers[name] = SimpleTimer()
        self._timers[name].start()

    def stop_timer(self, name):
        timer = self._timers.pop(name)
        timer.stop()
        self.report(name, timer.elapsed_time())

    def system_monitor(self, path, interval):
        return SystemMonitor(path, interval)

    def device_monitor(self, path, index, interval):
        return DeviceMonitor(path, index, interval)


class RepeatedTimer(Timer):

    def __init__(self, interval, *args, **kwargs):
        super(RepeatedTimer, self).__init__(interval, self.run)
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.daemon = True

    def run(self):
        while not self.finished.wait(self.interval):
            self._run(*self.args, **self.kwargs)


class SystemMonitor(RuntimeMonitor, RepeatedTimer):

    def __init__(self, path, interval):
        RuntimeMonitor.__init__(self, path)
        RepeatedTimer.__init__(self, interval)
        RuntimeMonitor.start(self)
        self.spec = HostSpec()
        self.report('system_info', self.spec.get_sys_info())

    def _run(self):
        self.report('system_state', self.spec.get_sys_state())

    def start(self):
        RepeatedTimer.start(self)

    def stop(self):
        super().stop()
        self.cancel()


class DeviceMonitor(RuntimeMonitor, RepeatedTimer):

    def __init__(self, path, index, interval):
        RuntimeMonitor.__init__(self, path)
        RepeatedTimer.__init__(self, interval)
        RuntimeMonitor.start(self)
        self.spec = DeviceSpec(index)
        self.report('device_info', self.spec.get_device_info())

    def _run(self):
        self.report('device_state', self.spec.get_device_state())

    def start(self):
        RepeatedTimer.start(self)

    def stop(self):
        super().stop()
        self.cancel()
