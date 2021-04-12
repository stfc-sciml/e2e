import click
import h5py
import numpy as np
from pathlib import Path
from skimage.transform import resize
from e2e_benchmark.constants import IMAGE_H, IMAGE_W
from e2e_benchmark.monitor.logger import MultiLevelLogger
from e2e_benchmark.preprocessing.image import ImageLoader


def load_arrays(path: Path):
    """ Load a dictionary of data from the NetCDF files"""
    loader = ImageLoader(path)

    bts = loader.load_bts().to_array().values
    rads = loader.load_radiances().to_array().values
    refs = loader.load_reflectances().to_array().values
    flags = loader.load_flags()
    bayes = flags.bayes_in.values
    summary = flags.summary_cloud.values
    day = flags.day.values

    rads = np.transpose(rads, [1, 2, 0])
    refs = np.transpose(refs, [1, 2, 0])
    bts = np.transpose(bts, [1, 2, 0])
    bayes = np.expand_dims(bayes, -1)
    summary = np.expand_dims(summary, -1)

    rads = np.nan_to_num(rads)
    bts = np.nan_to_num(bts)
    refs = np.nan_to_num(refs)
    bayes = np.nan_to_num(bayes)
    summary = np.nan_to_num(summary)

    # Resize to 1km grid
    rads = resize(rads, (IMAGE_H, IMAGE_W))
    refs = resize(refs, (IMAGE_H, IMAGE_W))
    bts = resize(bts, (IMAGE_H, IMAGE_W))

    bayes[bayes > 0] = 1
    bayes = bayes.astype(np.uint8) * 255
    summary[summary > 0] = 1
    summary = summary.astype(np.uint8) * 255

    bayes = resize(bayes, (IMAGE_H, IMAGE_W), anti_aliasing=False, preserve_range=True)
    summary = resize(summary, (IMAGE_H, IMAGE_W), anti_aliasing=False, preserve_range=True)

    return dict(rads=rads, refs=refs, bts=bts, bayes=bayes, summary=summary, day=day)


def do_conversion(path: Path, output_path: Path):
    # Check if file already exists, if so skip
    if ((output_path / Path('day') / path.name).exists() or
            (output_path / Path('night') / path.name).exists()):
        return

    data = load_arrays(path)

    folder = 'day' if np.all(data['day']) > 0 else 'night'
    folder = output_path / folder
    folder.mkdir(parents=True, exist_ok=True)

    output_file = (folder / path.name).with_suffix('.hdf')

    with h5py.File(output_file, 'w') as handle:
        handle.create_dataset("bts", data=data['bts'])
        handle.create_dataset("rads", data=data['rads'])
        handle.create_dataset("refs", data=data['refs'])
        handle.create_dataset("bayes", data=data['bayes'])
        handle.create_dataset("summary", data=data['summary'])


def convert_to_hdf(path: Path, output_path: Path, n_jobs: int = 8):
    paths = list(path.glob('*.SEN3'))

    logger = MultiLevelLogger(output_path / 'preprocessing_logs.txt')

    logger.begin('Preprocessing raw SLSTR products')
    for path in paths:
        do_conversion(path, output_path=output_path)
        logger.message(f'Finished processing {path}')

    logger.ended('Preprocessing raw SLSTR products')


def prepare(input_path: Path, output_path: Path):
    input_path = Path(input_path)

    if not input_path.exists():
        click.Abort('The input path {} does not exist!'.format(input_path))

    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)

    convert_to_hdf(input_path, output_path)
