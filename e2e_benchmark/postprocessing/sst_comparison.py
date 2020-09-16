import h5py
import click
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from sklearn.metrics import accuracy_score
from e2e_benchmark.constants import MIN_SST


class AlgorithmType:
    N2 = 1
    N3 = 3
    D2 = 4
    D3 = 5

    @staticmethod
    def get_type(method):
        if method == 0:
            return AlgorithmType.N2
        elif method == 1:
            return AlgorithmType.N3
        elif method == 2:
            return AlgorithmType.D2
        elif method == 3:
            return AlgorithmType.D3


def load_ssts_matchups(sst_file):
    sst_matchups = pd.read_hdf(sst_file)
    sst_matchups = sst_matchups.rename({name: name.lower() for name in sst_matchups.columns}, axis=1)

    ssts_filtered = sst_matchups.copy()
    ssts_filtered['isst_fixed'] = ssts_filtered.isst + 273.15

    # Filter out mis-aligned pixels outside of regridding window
    ssts_filtered = ssts_filtered.loc[(ssts_filtered.slat - ssts_filtered.latitude_an).abs() < 0.005]
    ssts_filtered = ssts_filtered.loc[(ssts_filtered.slon - ssts_filtered.longitude_an).abs() < 0.01]
    # filter out SST which are filled/not physical
    ssts_filtered = ssts_filtered.loc[ssts_filtered.isst_fixed > MIN_SST]
    # filter out satellite zenith angles less than 55 degrees
    ssts_filtered = ssts_filtered.loc[(ssts_filtered.satzan <= 55) & (ssts_filtered.satzao <= 55)]
    # filter out quality < 5
    # ssts_filtered = ssts_filtered.loc[ssts_filtered.quality_level == 5]
    return ssts_filtered


def robust_std(x):
    """
    RSD is calculated as 1.4826 * median_abs_dev(x)
    Median_abs_dev is median( abs( x-middle ) ) where middle = median(x)
    """
    middle = x.median()
    rsd = 1.4826 * (x - middle).abs().median()
    return rsd


def get_sst_diff(df, method):
    df = df.loc[df.sst_algorithm_type == AlgorithmType.get_type(method)]

    sst_i = df.isst_fixed
    sst_s = df['sat_sst_{}'.format(method)]

    sst_i = sst_i.loc[sst_s > MIN_SST]
    sst_s = sst_s.loc[sst_s > MIN_SST]

    diff = sst_s - sst_i

    return diff, sst_s, sst_i


@click.command()
@click.argument('sst-file')
@click.argument('output-dir')
def main(sst_file, output_dir):
    output_dir = Path(output_dir)
    mask_files = list(Path(output_dir).glob("S3A*.h5"))
    mask_file_names = list(map(lambda x: x.name, mask_files))

    sst_df = load_ssts_matchups(sst_file)

    # rename the file names to match the mask file names
    cems_files = sst_df.cems_path.map(lambda x: Path(x).name)
    cems_files = cems_files.map(lambda x: str(Path(x).with_suffix('.h5')))

    sst_df['local_file'] = cems_files
    sst_df['model_mask'] = np.NaN

    # select only the SST matchups we have files for
    sst_df = sst_df.loc[sst_df.local_file.isin(mask_file_names)]

    for file_name in tqdm(mask_files):
        # read the mask from disk
        with h5py.File(file_name, 'r') as handle:
            mask = handle['mask'][:]

        subset = sst_df.loc[sst_df.local_file == file_name.name]
        values = mask[0, subset.y_cems, subset.x_cems]
        sst_df.loc[sst_df.local_file == file_name.name, 'model_mask'] = values

    # find difference between Bayesian mask and SST ground truth
    bayes_ssts = sst_df.loc[(sst_df.pcloudn < .9) & (sst_df.pcloudo < .9)]
    diff, sst_s, sst_i = get_sst_diff(bayes_ssts, 2)
    median = diff.median()
    RSD = robust_std(diff)

    print("Bayesian median {:.4f}".format(median))
    print("Bayesian RSD {:.4f}".format(RSD))

    # find difference between UNet mask and SST ground truth
    unet_ssts = sst_df.loc[sst_df.model_mask < .5]
    diff, sst_s, sst_i = get_sst_diff(unet_ssts, 2)
    median = diff.median()
    RSD = robust_std(diff)

    print("UNet median {:.4f}".format(median))
    print("UNet RSD {:.4f}".format(RSD))

    bayes_unet_agreement = accuracy_score(sst_df.model_mask > .5, sst_df.bayes_in > .5)
    print("Bayes/UNet Mask Agreement: {:.2f}".format(bayes_unet_agreement))

    sst_df.to_hdf(output_dir / 'sst_predictions.h5', key='data')


if __name__ == "__main__":
    main()
