import click
from pathlib import Path


@click.group()
def cli():
    pass


@click.command()
@click.argument('input-file')
@click.argument('output-path')
def extract(input_file, output_path):
    from e2e_benchmark.preprocessing.extraction import extract
    extract(input_file, output_path)


@click.command()
@click.argument('input-path')
@click.argument('output-path')
def convert_hdf(input_path, output_path):
    from e2e_benchmark.preprocessing.convert_netcdf import prepare
    prepare(input_path, output_path)


@cli.command()
@click.argument('data-path')
@click.argument('output-path')
@click.option('--cpu-only', default=False, is_flag=True, type=bool)
def train(data_path, output_path, cpu_only=False):
    data_path = Path(data_path)

    if not data_path.exists():
        click.Abort('The data path {} does not exist!'.format(data_path))

    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)

    if cpu_only:
        import os
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    from e2e_benchmark.train import train_model
    train_model(data_path, output_path)


@click.command()
@click.argument('model-file')
@click.argument('data-dir')
@click.argument('output-dir')
def inference(model_file, data_dir, output_dir):
    from e2e_benchmark.postprocessing import main
    main(model_file, data_dir, output_dir)


@click.command()
@click.argument('sst-file')
@click.argument('output-dir')
def sst_comp(sst_file, output_dir):
    from e2e_benchmark.postprocessing.sst_comparison import main
    main(sst_file, output_dir)


if __name__ == "__main__":
    cli()
