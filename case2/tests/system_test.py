import pytest
from pathlib import Path
from click.testing import CliRunner
from e2e_benchmark import command as cmd


@pytest.fixture()
def raw_data_dir():
    return Path('data/test_data/pixbox').absolute()


@pytest.fixture()
def sst_data_dir():
    return Path('data/test_data/ssts/').absolute()


def test_commands_end_to_end(raw_data_dir, sst_data_dir):
    runner = CliRunner()

    with runner.isolated_filesystem():
        hdf_dir = Path('hdf')                        # Folder to output HDF conversions
        output_dir = Path('train')                    # Folder to output artifacts of training
        sst_file = sst_data_dir / 'sst_matchups.h5'  # SST matchup file location

        # Run each step sequentially, checking the output of one step correctly feeds into the next
        perform_convert_to_hdf(runner, raw_data_dir, hdf_dir / 'train')
        perform_convert_to_hdf(runner, sst_data_dir, hdf_dir / 'infer')
        perform_train(runner, hdf_dir / 'train', output_dir)
        perform_inference(runner, hdf_dir / 'infer', output_dir)
        perform_sst_comp(runner, sst_file, output_dir)


def perform_convert_to_hdf(runner, raw_data_dir, hdf_dir):
    assert raw_data_dir.exists()

    # Run HDF conversion command to transform .SEN3 folders -> .hdf
    result = runner.invoke(cmd.convert_hdf, [str(raw_data_dir), str(hdf_dir)])

    # Check command executed correctly
    assert not result.exception
    assert result.exit_code == 0

    assert hdf_dir.exists()


def perform_train(runner, hdf_dir, train_dir):
    # Run train model on HDF files
    result = runner.invoke(cmd.train, [str(hdf_dir), str(train_dir), '--epochs', '1'])

    # Check command executed correctly
    assert not result.exception
    assert result.exit_code == 0

    # Check data was written correctly
    assert train_dir.exists()
    assert (train_dir / 'model.h5').exists()


def perform_inference(runner, hdf_dir, infer_dir):
    # Run perform inference on HDF files
    result = runner.invoke(cmd.inference, [str(hdf_dir), str(infer_dir)])

    # Check command executed correctly
    assert not result.exception
    assert result.exit_code == 0


def perform_sst_comp(runner, sst_file, infer_dir):
    # Run perform inference on HDF files
    result = runner.invoke(cmd.sst_comp, [str(sst_file), str(infer_dir)])

    # Check command executed correctly
    assert not result.exception
    assert result.exit_code == 0

    assert (infer_dir / 'sst_predictions.h5').exists()

