import click
import zipfile
from pathlib import Path
from functools import partial
from multiprocessing import Pool
from tqdm import tqdm


def do_extraction(path: Path, output_path: Path):
    if path.exists():
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(output_path)


def extract_files(file_names, output_path: Path, n_jobs: int = 8):
    func = partial(do_extraction, output_path=output_path)
    with Pool(processes=n_jobs) as pool:
        for _ in tqdm(pool.imap_unordered(func, file_names), total=len(file_names)):
            pass

@click.command()
@click.argument('input-file')
@click.argument('output-path')
def extract(input_file, output_path):
    input_file = Path(input_file)

    if not input_file.exists():
        click.Abort('The input file {} does not exist!'.format(input_file))

    with input_file.open('r') as handle:
        file_names = handle.readlines()
        file_names = [Path(name.strip()) for name in file_names]

    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)

    extract_files(file_names, output_path)

if __name__ == "__main__":
    extract()
