import time
import logging


class SimpleTimer:

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def elapsed_time(self):
        return self.end_time - self.start_time


class MultiLevelLogger:

    def __init__(self, path):
        self._timers = []
        self._current_level = 0
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(logging.INFO)

        self._logger = logging.getLogger('test')
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(file_handler)

    def begin(self, proc_name, indent_fill='.'):
        timer = SimpleTimer()
        timer.start()
        self._timers.append(timer)

        message = [indent_fill * self._current_level * 4, "<BEGIN> ",  proc_name]
        message = ''.join(message)

        self._logger.info(message)
        self._current_level += 1

    def ended(self, proc_name, indent_fill='.'):
        self._current_level -= 1

        timer = self._timers.pop()
        timer.stop()
        elapsed = timer.elapsed_time()
        message = [indent_fill * self._current_level * 4, "<END> ",  proc_name, f" [ELAPSED = {elapsed: .2f} sec]"]
        message = ''.join(message)

        self._logger.info(message)

    def message(self, what, indent_fill='.'):
        message = [indent_fill * self._current_level * 4, "<MESSG> ",  what]
        message = ''.join(message)
        self._logger.info(message)
