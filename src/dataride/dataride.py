from collections import defaultdict

import click

from .utils import (
    prepare_jinja_environment,
    load_config,
    run_resource_check,
    update_resource_dict_with_defaults,
    load_template,
    render_jinja,
    fill_template_values,
    create_result_dir_structure,
    save_module_setup,
    save_env_setup,
    fetch_resource_variables,
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
    config_main = load_config(config_path, is_main=True)
    output_dict = defaultdict(lambda: {"main.tf": "", "var.tf": ""})

    for resource in config_main["resources"]:

        run_resource_check(resource)
        resource_type = next(iter(resource))

        resource_updated = update_resource_dict_with_defaults(resource, resource_type)
        resource_module = resource_updated[resource_type]["_module"]

        resource_template = load_template(resource_type)
        if resource[resource_type]["_jinja"]:
            resource_template = render_jinja(resource_template, resource_updated[resource_type], jinja_environment)

        resource_template_filled = fill_template_values(resource_template, resource_updated[resource_type])
        output_dict[resource_module]["main.tf"] += resource_template_filled + "\n" * 2

        resource_variables = fetch_resource_variables(resource_updated[resource_type], jinja_environment)
        output_dict[resource_module]["var.tf"] += resource_variables[0]

        # Adding module information to the config dictionary
        if resource_module not in config_main["modules"].keys():
            config_main["modules"][resource_module] = {
                "vars_with_def": [],
                "vars_no_def": [],
            }

        config_main["modules"][resource_module]["vars_with_def"] += resource_variables[1]
        config_main["modules"][resource_module]["vars_no_def"] += resource_variables[2]

    create_result_dir_structure(destination)

    for module in output_dict.keys():
        save_module_setup(destination, module, output_dict[module])

    # TODO: Add different environments creation
    env_main = load_template("env_main")
    env_main = render_jinja(env_main, config_main, jinja_environment)
    save_env_setup(destination, env_main)
