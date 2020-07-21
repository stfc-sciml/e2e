import click
from pathlib import Path

from e2e_benchmark.train import train_model
from e2e_benchmark.preprocessing.convert_netcdf import convert_netcdf
from e2e_benchmark.preprocessing.extraction import extract_files


@click.group()
def cli():
    pass


@cli.command()
@click.argument('input-file')
@click.argument('output-path')
def extract(input_file, output_path):
    input_file = Path(input_file)

    if not input_file.exists():
        click.Abort('The input file {} does not exist!'.format(input_file))

    with input_file.open('r') as handle:
        file_names = handle.readlines()

    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)

    extract_files(file_names, output_path)


@cli.command()
@click.argument('input-path')
@click.argument('output-path')
def prepare(input_path, output_path):
    input_path = Path(input_path)

    if not input_path.exists():
        click.Abort('The input path {} does not exist!'.format(input_path))

    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)

    convert_netcdf(input_path, output_path)


@cli.command()
@click.argument('data-path')
@click.argument('output-path')
def train(data_path, output_path):
    data_path = Path(data_path)

    if not data_path.exists():
        click.Abort('The data path {} does not exist!'.format(data_path))

    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True, parents=True)

    train_model(data_path, output_path)


if __name__ == "__main__":
    cli()
