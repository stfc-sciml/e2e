import h5py
import click
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from e2e_benchmark.constants import MIN_SST


def load_ssts_matchups(sst_file):
    sst_matchups = pd.read_hdf(sst_file)
    sst_matchups = sst_matchups.rename({name: name.lower() for name in sst_matchups.columns}, axis=1)

    ssts_filtered = sst_matchups.copy()
    # print(all_ssts.shape)
    ssts_filtered['isst_fixed'] = ssts_filtered.isst + 273.15

    # Filter out mis-aligned pixels
    ssts_filtered = ssts_filtered.loc[(ssts_filtered.slat - ssts_filtered.latitude_an).abs() < 0.005]
    ssts_filtered = ssts_filtered.loc[(ssts_filtered.slon - ssts_filtered.longitude_an).abs() < 0.01]

    # filter out SST which are filled/not physical
    ssts_filtered = ssts_filtered.loc[ssts_filtered.isst_fixed > MIN_SST]
    # filter out satellite zenith angles less than 55 degrees
    ssts_filtered = ssts_filtered.loc[(ssts_filtered.satzan <= 55) & (ssts_filtered.satzao <= 55)]
    # filter out quality < 5
    # ssts_filtered = ssts_filtered.loc[ssts_filtered.quality_level == 5]
    return ssts_filtered


@click.command()
@click.argument('sst-file')
@click.argument('output-dir')
def main(sst_file, output_dir):
    output_dir = Path(output_dir)

    sst_df = load_ssts_matchups(sst_file)

    mask_files = list(Path(output_dir).glob("S3A*.h5"))

    cems_files = sst_df.cems_path.map(lambda x: Path(x).name)
    cems_files = cems_files.map(lambda x: Path(x).with_suffix('.h5'))

    sst_df['local_file'] = cems_files
    sst_df['model_mask'] = 0

    for file_name in tqdm(mask_files):
        # read the mask from disk
        with h5py.File(file_name, 'r') as handle:
            mask = handle['mask'][:]

        subset = sst_df.loc[sst_df.local_file == file_name.name]
        values = mask[0, subset.y_cems, subset.x_cems]
        sst_df.loc[sst_df.local_file == file_name.name, 'model_mask'] = values

    sst_df.to_hdf(output_dir / 'sst_predictions.h5', key='data')


if __name__ == "__main__":
    main()
