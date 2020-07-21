import click
from pathlib import Path

from e2e_benchmark.train import train_model


@click.group()
def cli():
    pass


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
