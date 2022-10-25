import os
import yaml
import logging
import subprocess
from random import randint
from typing import Dict, Tuple, List, Set

from jinja2 import Environment as JinjaEnvironment

# TODO: Move it somewhere else in the future
VARIABLES_DEFAULT_DICT = {"default_value": None, "description": ""}


def log_if_verbose(message: str, verbose: bool) -> None:
    """
    Checks whether a programme is running in verbose mode and, if applicable,
        logs information according to the logging level
    :param message: message string to be logged
    :param verbose: whether to print more outputs
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("dr")
    if verbose:
        logger.info(message)


def format_terraform_code(destination: str) -> None:
    """
    Executes `terraform fmt` in a destination directory
    :param destination: directory location for infrastructure setup generation
    """
    subprocess.run(["terraform", "fmt", "-recursive", "-list=false", destination])


def prepare_jinja_environment() -> JinjaEnvironment:
    """
    Prepares a Jinja environment for templates processing.
    Additionally, provides a helper function for raising errors while rendering templates
    :return: JinjaEnvironment object
    """

    def raise_helper(msg: str):
        """
        Function helping to raise an error in Jinja environment while rendering
        :param msg: message to pass while raising an error
        """
        raise Exception(msg)

    def intersection(a: List[str], b: List[str]) -> List[str]:
        """
        Returns an intersection of 2 lists
        """
        return list(set(a) & set(b))

    env = JinjaEnvironment()
    env.globals["raise_error"] = raise_helper
    env.globals["intersection"] = intersection
    env.filters["any"] = any
    return env


def load_config(path: str, is_main: bool = False) -> Dict:
    """
    Loads a YAML dataride config file into a Python dictionary
    :param path: where config file is stored
    :param is_main: whether YAML file includes main dataride config or only resource config
    :return: Python dictionary with loaded template resources
    """
    with open(path) as f:
        config = yaml.safe_load(f.read())

    if is_main:
        config["modules"] = {}

    return config


def load_template(template_name: str) -> str:
    """
    Loads a Terraform template file from `infra_templates/` directory
    :param template_name: name of the template to load, e.g. aws_glue_crawler
    :return: string containing loaded template file
    """
    return open(f"infra_templates/{template_name}.tf").read()


def run_config_check(config: Dict, verbose: bool) -> None:
    """
    Checks basic information about dataride config dictionary
    :param config: config dictionary loaded from a yaml file
    :param verbose: whether to print more outputs
    """
    log_if_verbose("\tRunning main config file check...", verbose)

    assert all(type(provider) == dict for provider in config["providers"])

    # Provider checks
    provider_names_list = []
    for provider in config["providers"]:
        provider_name = next(iter(provider))
        provider_params = provider[provider_name]

        # Checking for duplicates
        if provider_name in provider_names_list:
            raise KeyError("Provider has been duplicated. Please verify your config file")
        else:
            provider_names_list.append(provider_name)

        # AWS provider checks
        if provider_name == "aws":
            assert "region" in provider_params.keys()

    log_if_verbose("\tConfig check passed!", verbose)


def run_resource_check(resource: Dict[str, Dict[str, str]], resource_type: str, verbose: bool) -> None:
    """
    Checks basic information about the resource.
    :param resource: current resource that is being prepared (dictionary loaded from yaml template file)
    :param resource_type: name of the resource to create, e.g. aws_glue_crawler
    :param verbose: whether to print more outputs
    """
    log_if_verbose(f"\tRunning resource config check for {resource_type}...", verbose)

    assert len(resource) == 1

    log_if_verbose("\tResource config check passed!", verbose)


def update_resource_dict_with_defaults(
    resource_dict: Dict[str, str], resource_type: str, create_resource_name: bool = True
) -> Dict:
    """
    Extra process of updating resource dictionary with default values if possible (in case some of them were skipped),
        especially, creating a resource name for Terraform in case it wasn't specified
    :param resource_dict: dictionary with details of the current resource that is being prepared
    :param resource_type: name of the resource to create, e.g. aws_glue_crawler
    :param create_resource_name: whether to create a resource name (not applicable for main config update)
    :return: resource dictionary with default values appended where possible
    """
    # Updating resource object with default values if applicable
    resource_defaults = load_config(f"./infra_defaults/{resource_type}.yaml")
    resource_defaults = {k: v for k, v in resource_defaults.items() if k not in resource_dict.keys()}
    if resource_defaults:
        resource_dict.update(resource_defaults)

    # Creating a resource name for Terraform if wasn't specified
    if create_resource_name and resource_dict.get("resource_name", None) is None:
        resource_dict["resource_name"] = resource_type + "_" + str(randint(10**4, 9 * 10**4))

    return resource_dict


def render_jinja(
    template: str,
    values_dict: Dict[str, str],
    jinja_environment: JinjaEnvironment,
) -> str:
    """
    Renders Jinja language inside a template file
    :param template: resource template file content read from `infra_templates/` directory
    :param values_dict: dictionary that contains values to be possibly filled inside Jinja template
    :param jinja_environment: Jinja Python framework environment to process template
    :return: resource in form of a simple string that should be forwarded to value filling process
    """
    jinja_template = jinja_environment.from_string(template)
    return jinja_template.render(values_dict)


def fill_template_values(template: str, values_dict: Dict) -> str:
    """
    Fills values inside a resource template file,
        in place of any param inside angle brackets: `<`, and `>`,
        fills value that is fetched either from provided config file (priority) or default values dictionary
    :param template: resource template file content (read from `infra_templates/` directory),
        after Jinja processing if applicable
    :param values_dict: dictionary containing values to fill within a template
    :return: template with filled values. It shouldn't contain any angle bracket whatsoever after this step
    """
    for param, value in values_dict.items():
        if type(value) == bool or param == "type":
            template = template.replace(f"<{param}>", f"{str(value).lower()}")
        elif type(value) == str:
            if value.startswith("_"):
                template = template.replace(f"<{param}>", f"{str(value)[1:]}")
            else:
                template = template.replace(f"<{param}>", f'"{str(value)}"')
        elif type(value) == int or type(value) == float:
            template = template.replace(f"<{param}>", f"{str(value)}")
        elif type(value) == dict and value["is_variable"]:
            template = template.replace(f"<{param}>", f"var.{str(value['name'])}")
        elif value is None:
            pass  # do nothing, but don't raise error
        else:
            raise ValueError(f"Wrong resource parameter value type for {param}")

    return template


def fetch_resource_variables(
    resource_dict: Dict, jinja_environment: JinjaEnvironment
) -> Tuple[str, List[str], List[str]]:
    """
    Fetching information about all Terraform resource variables that were provided inside main config file
    :param resource_dict: current resource that is being prepared (dictionary loaded from yaml template file)
    :param jinja_environment: Jinja Python framework environment to process template
    :return: a tuple of: rendered template, list of variable names with default values,
        and list of variable names without default values
    """
    result_str, vars_with_def, vars_no_def = "", [], []

    # Only iterating over parameters which were specified as variables in the main config file
    for param, value in resource_dict.items():
        if type(value) == dict and value.get("is_variable", False):
            missing_defaults = {k: v for k, v in VARIABLES_DEFAULT_DICT.items() if k not in value.keys()}
            value.update(missing_defaults)

            # Render variable template for var.tf for each module
            var_template = load_template("var")
            rendered = render_jinja(var_template, value, jinja_environment)
            result_str += fill_template_values(rendered, value) + "\n" * 2

            # Append variable name to proper list (for module instantiating inside TF environment)
            if value["default_value"] is None:
                vars_no_def.append(value["name"])
            else:
                vars_with_def.append(value["name"])

    return result_str, vars_with_def, vars_no_def


def create_result_dir_structure(destination: str) -> None:
    """
    Creates a result directory structure:
        - `destination` directory
        - Terraform modules directory
    If a `destination` directory exists, function breaks
    :param destination: directory location for infrastructure setup generation
    """
    try:
        os.mkdir(destination)
        os.mkdir(f"{destination}/modules")
    except OSError as error:
        logging.error(error)
        exit(1)


def save_module_setup(destination: str, module: str, module_output: Dict[str, str], verbose: bool) -> None:
    """
    Saves infrastructure module setup code into the specified location
    If a `module` directory exists, function breaks
    :param destination: directory location for infrastructure setup generation
    :param module: what module setup to save
    :param module_output: module main output string that contains whole Infrastructure as a Code setup
    :param verbose: whether to print more outputs
    """
    log_if_verbose(f"\tSaving module: {module}...", verbose)

    try:
        os.mkdir(f"{destination}/modules/{module}")
    except OSError as error:
        logging.error(error)
        exit(1)

    with open(f"{destination}/modules/{module}/main.tf", "w") as f:
        f.write(module_output["main.tf"])

    if module_output["var.tf"]:
        with open(f"{destination}/modules/{module}/var.tf", "w") as f:
            f.write(module_output["var.tf"])

    log_if_verbose(f"\tModule saved!", verbose)


def save_env_setup(destination: str, env_name: str, env_dict: Dict, verbose: bool) -> None:
    """
    Saves infrastructure environment setup code into the specified location
    If an environment directory exists, function breaks
    :param destination: directory location for infrastructure setup generation
    :param env_name: name of the environment to save
    :param env_dict: environment dictionary containing information including main.tf and var.tf strings
    :param verbose: whether to print more outputs
    """
    log_if_verbose(f"\tSaving environment: {env_name}...", verbose)

    try:
        os.mkdir(f"{destination}/{env_name}")
    except OSError as error:
        logging.error(error)
        exit(1)

    with open(f"{destination}/{env_name}/main.tf", "w") as f:
        f.write(env_dict["main.tf"])

    if env_dict["var.tf"]:
        with open(f"{destination}/{env_name}/var.tf", "w") as f:
            f.write(env_dict["var.tf"])

    log_if_verbose(f"\tEnvironment saved!", verbose)


def prepare_action_required(
    config_main: Dict,
    jinja_environment: JinjaEnvironment,
    destination: str,
    action_required_path: str = "assets/action_required.md",
) -> None:
    """
    Prepares action-required document for users after infrastructure generation
    :param config_main: main dataride configuration dictionary
    :param jinja_environment: Jinja Python framework environment to process template
    :param destination: directory location for infrastructure setup generation
    :param action_required_path: location where action required template document is stored
    :return:
    """
    with open(action_required_path) as f:
        action_required_rendered = render_jinja(f.read(), config_main, jinja_environment)

    with open(f"{destination}/action_required.md", "w") as f:
        f.write(action_required_rendered)
