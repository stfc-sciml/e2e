import click
import h5py
import numpy as np
from functools import partial
from tqdm import tqdm
from pathlib import Path
from multiprocessing import Pool
from skimage.transform import resize
from e2e_benchmark.constants import IMAGE_H, IMAGE_W
from e2e_benchmark.preprocessing.image import ImageLoader


def do_conversion(path: Path, output_path: Path):
    # Check if file already exists, if so skip
    if ((output_path / Path('day') / path.name).exists() or
            (output_path / Path('night') / path.name).exists()):
        return

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

    folder = 'day' if np.all(day) > 0 else 'night'
    folder = output_path / folder
    folder.mkdir(parents=True, exist_ok=True)

    output_file = (folder / path.name).with_suffix('.hdf')

    with h5py.File(output_file, 'w') as handle:
        handle.create_dataset("bts", data=bts)
        handle.create_dataset("rads", data=rads)
        handle.create_dataset("refs", data=refs)
        handle.create_dataset("bayes", data=bayes)
        handle.create_dataset("summary", data=summary)


def convert_netcdf(path: Path, output_path: Path, n_jobs: int = 8):
    paths = list(path.glob('**/*.SEN3'))

    func = partial(do_conversion, output_path=output_path)
    with Pool(processes=n_jobs) as pool:
        for _ in tqdm(pool.imap_unordered(func, paths), total=len(paths)):
            pass


def prepare(input_path, output_path):
    input_path = Path(input_path)

    if not input_path.exists():
        click.Abort('The input path {} does not exist!'.format(input_path))

    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)

    convert_netcdf(input_path, output_path)
