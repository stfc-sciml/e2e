import pytest
from pathlib import Path
from click.testing import CliRunner
from e2e_benchmark import command as cmd


@pytest.fixture()
def raw_data_dir():
    return Path('../data/pixbox').absolute()


@pytest.fixture()
def sst_data_dir():
    return Path('../data/ssts/').absolute()


def test_commands_end_to_end(raw_data_dir, sst_data_dir):
    runner = CliRunner()

    with runner.isolated_filesystem():
        hdf_dir = Path('hdf')                        # Folder to output HDF conversions
        train_dir = Path('train')                    # Folder to output artifacts of training
        infer_dir = Path('infer')                    # Folder to output artifacts of inference
        model_file = (train_dir / 'model.h5')        # Model file name produced during train step
        sst_file = sst_data_dir / 'sst_matchups.h5'  # SST matchup file location

        # Run each step sequentially, checking the output of one step correctly feeds into the next
        perform_convert_to_hdf(runner, raw_data_dir, hdf_dir)
        perform_train(runner, hdf_dir, train_dir)
        perform_inference(runner, model_file, hdf_dir, infer_dir)
        perform_sst_comp(runner, sst_file, infer_dir)


def perform_convert_to_hdf(runner, raw_data_dir, hdf_dir):
    assert raw_data_dir.exists()

    # Run HDF conversion command to transform .SEN3 folders -> .hdf
    result = runner.invoke(cmd.convert_hdf, [str(raw_data_dir), str(hdf_dir)])

    # Check command executed correctly
    assert not result.exception
    assert result.exit_code == 0

    # Check data was written correctly
    assert hdf_dir.exists()
    assert len(list(hdf_dir.glob('**/*.hdf'))) == 2


def perform_train(runner, hdf_dir, train_dir):
    # Run train model on HDF files
    result = runner.invoke(cmd.train, [str(hdf_dir), str(train_dir), '--epochs', '1'])

    # Check command executed correctly
    assert not result.exception
    assert result.exit_code == 0

    # Check data was written correctly
    assert train_dir.exists()
    assert (train_dir / 'model.h5').exists()


def perform_inference(runner, model_file, hdf_dir, infer_dir):
    # Run perform inference on HDF files
    result = runner.invoke(cmd.inference, [str(model_file), str(hdf_dir), str(infer_dir)])

    # Check command executed correctly
    assert not result.exception
    assert result.exit_code == 0

    # Check data was written correctly
    assert len(list(infer_dir.glob('**/*.h5'))) == 2


def perform_sst_comp(runner, sst_file, infer_dir):
    # Run perform inference on HDF files
    result = runner.invoke(cmd.sst_comp, [str(sst_file), str(infer_dir)])

    # Check command executed correctly
    assert not result.exception
    assert result.exit_code == 0

    assert (infer_dir / 'sst_predictions.h5').exists()
