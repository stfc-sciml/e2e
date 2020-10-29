import time
import logging


class SimpleTimer:
    """A simple timer for logging the elasped duration"""

    def start(self):
        """Start the timer"""
        self.start_time = time.time()

    def stop(self):
        """Stop the timer"""
        self.end_time = time.time()

    def elapsed_time(self) -> float:
        """Get the total elapsed time as a string

        @return: elapsed time
        """
        return self.end_time - self.start_time


class MultiLevelLogger:
    """A class to log text to file with multiple levels of indentation"""

    def __init__(self, path: str, indent_fill: str = '.'):
        """Create a new multi level logger instance

        @param path: file path to save logs to.
        @param indent_fill: indent to fill different process levels (default='.')
        """
        self._timers = []
        self._current_level = 0
        self._indent_fill = indent_fill
        file_handler = logging.FileHandler(path)
        file_handler.setLevel(logging.INFO)

        self._logger = logging.getLogger('test')
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(file_handler)

    def begin(self, proc_name: str):
        """Begin logging a sub-process

        @param proc_name: name of the sub-process
        """
        timer = SimpleTimer()
        timer.start()
        self._timers.append(timer)

        message = [self._indent_fill * self._current_level * 4, "<BEGIN> ", proc_name]
        message = ''.join(message)

        self._logger.info(message)
        self._current_level += 1

    def ended(self, proc_name: str):
        """Finish logging a sub-process

        @param proc_name:  name of the sub-process
        """
        self._current_level -= 1

        timer = self._timers.pop()
        timer.stop()
        elapsed = timer.elapsed_time()
        message = [self._indent_fill * self._current_level * 4, "<END> ", proc_name, f" [ELAPSED = {elapsed: .2f} sec]"]
        message = ''.join(message)

        self._logger.info(message)

    def message(self, what: str):
        """ Log a message to from the current sub-process

        @param what: message text to log
        """
        message = [self._indent_fill * self._current_level * 4, "<MESSG> ", what]
        message = ''.join(message)
        self._logger.info(message)
