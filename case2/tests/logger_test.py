import os
import time

from e2e_benchmark.monitor.logger import SimpleTimer, MultiLevelLogger


def test_simple_timer():
    timer = SimpleTimer()
    timer.start()
    time.sleep(1)
    timer.stop()
    assert timer.elapsed_time() > 1


def test_logger(tmp_path):
    log_file_name = tmp_path / 'test.log'

    logger = MultiLevelLogger(log_file_name)
    logger.begin('Process Father')
    logger.message('Father says something')

    logger.begin('Process Child A')
    logger.message('Child A says something')
    logger.ended('Process Child A')

    logger.begin('Process Child B')
    logger.message('Child B says something')
    logger.ended('Process Child B')

    logger.message('Father conclude with something')
    logger.ended('Process Father')

    assert os.path.exists(log_file_name)

    # Check output matches the expected format
    test_output = """<BEGIN> Process Father
....<MESSG> Father says something
....<BEGIN> Process Child A
........<MESSG> Child A says something
....<END> Process Child A [ELAPSED =
....<BEGIN> Process Child B
........<MESSG> Child B says something
....<END> Process Child B [ELAPSED =
....<MESSG> Father conclude with something
<END> Process Father [ELAPSED =
    """
    expected_output = test_output.strip().split('\n')
    actual_output = log_file_name.read_text()
    actual_output = actual_output.strip().split('\n')
    print(actual_output)
    assert len(expected_output) == len(actual_output)
    for i in range(len(expected_output)):
        assert expected_output[i] in actual_output[i]
