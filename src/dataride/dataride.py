import click

from dataride.application import Application


@click.group()
def main():
    """
    `dataride` is a Python package that enables creating data platform infrastructure
    within seconds for small/medium projects as well as PoCs (Proof of Concept).
    Its aim is to generate ready-to-deploy code for various frameworks incl. Terraform or Apache Airflow.
    """


@main.command()
@click.option("--config_path", "-c", type=str, help="Where YAML data platform config setup file is stored")
@click.option("--destination", "-d", type=str, help="Where infrastructure code should be saved")
@click.option(
    "--fmt",
    type=bool,
    default=True,
    help="Whether to execute `terraform fmt` on a destination directory after infrastructure generation",
)
@click.option("--verbose", "-v", is_flag=True, type=bool, default=False, help="Whether to print more outputs")
def create(config_path: str, destination: str, fmt: bool = True, verbose: bool = False) -> None:
    """
    CLI command to generate data platform infrastructure code out of the provided template

    :param config_path: where YAML data platform config setup file is stored
    :param destination: where infrastructure code should be saved
    :param fmt: whether to execute `terraform fmt` on a destination directory after infrastructure generation
    :param verbose: whether to print more outputs
    """
    Application().create_infra_setup(config_path, destination, fmt, verbose)
