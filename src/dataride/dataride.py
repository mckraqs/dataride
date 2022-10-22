from collections import defaultdict

import click

from .utils import (
    log_if_verbose,
    format_terraform_code,
    prepare_jinja_environment,
    load_config,
    run_resource_check,
    run_config_check,
    update_resource_dict_with_defaults,
    load_template,
    render_jinja,
    fill_template_values,
    create_result_dir_structure,
    save_module_setup,
    save_env_setup,
    fetch_resource_variables,
    prepare_action_required,
)


@click.group()
def main():
    """
    Main interface gate, implemented for `click` framework purposes,
        to group functionalities into one logical entity
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
    CLI command to generate data platform infrastructure code out of provided template
    :param config_path: where YAML data platform config setup file is stored
    :param destination: where infrastructure code should be saved
    :param fmt: whether to execute `terraform fmt` on a destination directory after infrastructure generation
    :param verbose: whether to print more outputs
    """
    log_if_verbose("Starting a dataride!", verbose)

    jinja_environment = prepare_jinja_environment()
    config_main = load_config(config_path, is_main=True)
    config_main = update_resource_dict_with_defaults(config_main, "config_main", create_resource_name=False)
    output_dict = defaultdict(lambda: {"main.tf": "", "var.tf": ""})

    run_config_check(config_main, verbose)

    for resource in config_main["resources"]:

        resource_type = next(iter(resource))

        log_if_verbose(f"Processing resource: {resource_type}", verbose)
        run_resource_check(resource, resource_type, verbose)

        resource_updated = update_resource_dict_with_defaults(resource[resource_type], resource_type)
        resource_module = resource_updated["_module"]

        # Rendering template if applicable
        resource_template = load_template(resource_type)
        if resource[resource_type]["_jinja"]:
            resource_template = render_jinja(resource_template, resource_updated, jinja_environment)

        # Filling template with resource values for main.tf
        resource_template_filled = fill_template_values(resource_template, resource_updated)
        output_dict[resource_module]["main.tf"] += resource_template_filled + "\n" * 2

        # Filling template with resource values for var.tf
        resource_variables = fetch_resource_variables(resource_updated, jinja_environment)
        output_dict[resource_module]["var.tf"] += resource_variables[0]

        # Adding module information to the config dictionary for modules instantiating generation
        if resource_module not in config_main["modules"].keys():
            config_main["modules"][resource_module] = {
                "vars_with_def": [],
                "vars_no_def": [],
            }

        config_main["modules"][resource_module]["vars_with_def"] += resource_variables[1]
        config_main["modules"][resource_module]["vars_no_def"] += resource_variables[2]

        log_if_verbose(
            f"\tResource variables: with default values - {len(resource_variables[1])},"
            f" no default values - {len(resource_variables[2])}",
            verbose,
        )

    log_if_verbose("Saving infrastructure to passed location", verbose)
    create_result_dir_structure(destination)

    log_if_verbose("Saving modules", verbose)
    for module in output_dict.keys():
        save_module_setup(destination, module, output_dict[module], verbose)

    log_if_verbose("Saving environments", verbose)
    for env_name, env_config in config_main["envs"].items():
        env_template = load_template("env_default")
        if env_config is None:
            env_config = {"_empty": "_empty"}
        env_config["variables"] = [k for k, v in env_config.items() if type(v) == dict and v.get("is_variable", False)]

        env_config["var.tf"] = fetch_resource_variables(env_config, jinja_environment)[0]
        if env_config.get("backend", False):
            config_main["backend"] = env_config["backend"]
        else:
            config_main["backend"] = config_main["default_backend"]

        env_config["main.tf"] = render_jinja(
            env_template, {**config_main, **{"env": {**env_config}}}, jinja_environment
        )
        config_main["envs"][env_name] = env_config
        save_env_setup(destination, env_name, env_config, verbose)

    if fmt:
        log_if_verbose("Formatting Terraform code", verbose)
        format_terraform_code(destination)

    prepare_action_required(config_main, jinja_environment, destination)
