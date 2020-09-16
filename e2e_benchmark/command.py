import click
from pathlib import Path


@click.group()
def cli():
    pass


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


if __name__ == "__main__":
    cli()
