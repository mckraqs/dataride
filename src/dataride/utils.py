import os
import yaml
import logging
from random import randint
from typing import Dict, Tuple, List

from jinja2 import Environment as JinjaEnvironment

# TODO: Move it somewhere else in the future
VARIABLES_DEFAULT_DICT = {"default_value": None, "description": ""}


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

    env = JinjaEnvironment()
    env.globals["raise_error"] = raise_helper
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


def run_resource_check(resource: Dict[str, Dict[str, str]]) -> None:
    """
    Checks basic information about the resource
    :param resource: current resource that is being prepared (dictionary loaded from yaml template file)
    """
    assert len(resource) == 1


def update_resource_dict_with_defaults(
    resource: Dict[str, Dict[str, str]], resource_type: str
) -> Dict[str, Dict[str, str]]:
    """
    Extra process of updating resource dictionary with default values if possible (in case some of them were skipped),
        especially, creating a resource name for Terraform in case it wasn't specified
    :param resource: current resource that is being prepared (dictionary loaded from yaml template file)
    :param resource_type: name of the resource to create, e.g. aws_glue_crawler
    :return: resource dictionary with default values appended where possible
    """
    # Updating resource object with default values if applicable
    resource_defaults = load_config(f"./infra_defaults/{resource_type}.yaml")
    resource_defaults = {k: v for k, v in resource_defaults.items() if k not in resource[resource_type].keys()}
    if resource_defaults:
        resource[resource_type].update(resource_defaults)

    # Creating a resource name for Terraform if wasn't specified
    if resource[resource_type].get("resource_name", None) is None:
        resource[resource_type]["resource_name"] = resource_type + "_" + str(randint(10**4, 9 * 10**4))

    return resource


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
        if type(value) == str or type(value) == bool or value is None:
            template = template.replace(f"<{param}>", f'"{str(value)}"')
        elif type(value) == dict and value["is_variable"]:
            template = template.replace(f"<{param}>", f"var.{str(value['name'])}")
        else:
            raise ValueError("Wrong resource parameter value type")

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
        if type(value) == dict and value["is_variable"]:
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
    :param destination: where setup should be saved
    """
    try:
        os.mkdir(destination)
        os.mkdir(f"{destination}/modules")
    except OSError as error:
        logging.error(error)
        exit(1)


def save_module_setup(destination: str, module: str, module_output: Dict[str, str]) -> None:
    """
    Saves infrastructure module setup code into the specified location
    If a `module` directory exists, function breaks
    :param destination: where setup should be saved
    :param module: what module setup to save
    :param module_output: module main output string that contains whole Infrastructure as a Code setup
    """
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


def save_env_setup(destination: str, env_main: str) -> None:
    """
    Saves infrastructure environment setup code into the specified location
    If an environment directory exists, function breaks
    :param destination: where setup should be saved
    :param env_main: environment main output string that contains whole Infrastructure as a Code setup
    """
    try:
        os.mkdir(f"{destination}/env")
    except OSError as error:
        logging.error(error)
        exit(1)

    with open(f"{destination}/env/main.tf", "w") as f:
        f.write(env_main)
