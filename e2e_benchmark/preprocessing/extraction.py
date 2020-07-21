import zipfile
from pathlib import Path
from functools import partial
from multiprocessing import Pool
from tqdm import tqdm


def do_extraction(path: Path, output_path: Path):
    with zipfile.ZipFile(path, 'r') as zip_ref:
        output_name = (output_path / path.name).with_suffix('')
        zip_ref.extractall(output_name)


def extact_files(file_names, output_path: Path, n_jobs: int = 8):
    func = partial(do_extraction, output_path=output_path)
    with Pool(processes=n_jobs) as pool:
        for _ in tqdm(pool.imap_unordered(func, file_names), total=len(file_names)):
            pass
