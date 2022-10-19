import click
from collections import defaultdict

from .utils import (
    prepare_jinja_environment,
    load_config,
    run_resource_check,
    update_resource_with_defaults,
    load_template,
    render_jinja,
    fill_template_values,
    create_result_dir_structure,
    save_module_setup,
    save_env_setup,
)


@click.group()
def main():
    """
    Main interface gate, implemented for `click` framework purposes,
        to group functionalities into one logical entity
    """


@main.command()
@click.option("--config_path", "-c", type=str)
@click.option("--destination", "-d", type=str)
def create(
    config_path: str,
    destination: str,
) -> None:
    """
    CLI command to generate data platform infrastructure code out of provided template
    :param config_path: where YAML data platform config setup file is stored
    :param destination: where infrastructure code should be saved
    """
    jinja_environment = prepare_jinja_environment()
    output_dict = defaultdict(str)

    config = load_config(config_path)

    for resource in config["resources"]:

        run_resource_check(resource)
        resource_type = next(iter(resource))

        resource_updated = update_resource_with_defaults(resource, resource_type)
        resource_template = load_template(resource_type)
        if resource[resource_type]["_jinja"]:
            resource_template = render_jinja(resource_template, resource_updated[resource_type], jinja_environment)

        resource_template_filled = fill_template_values(resource_updated, resource_type, resource_template)
        output_dict[resource[resource_type]["_module"]] += resource_template_filled + "\n" * 2

    env_main = load_template("env_main")
    env_main = render_jinja(env_main, config, jinja_environment)

    create_result_dir_structure(destination)

    for module in output_dict.keys():
        save_module_setup(destination, module, output_dict[module])

    # TODO: Add different environments creation
    save_env_setup(destination, env_main)
