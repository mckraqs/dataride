import os
import yaml
import logging

from typing import Dict
from random import randint

from jinja2 import Environment as JinjaEnvironment


def raise_helper(msg: str) -> None:
    """
    Helper function to raise errors inside Jinja templates
    :param msg: message to pass inside the Exception object
    :return:
    """
    raise Exception(msg)


def prepare_jinja_environment() -> JinjaEnvironment:
    env = JinjaEnvironment()
    env.globals['raise_error'] = raise_helper
    return env


def load_config(path: str) -> Dict:
    """
    Loads a YAML (preferably dataride template) config file into a Python dictionary
    :param path: where config file is stored
    :return: Python dictionary with loaded template resources
    """
    with open(path) as f:
        return yaml.safe_load(f.read())


def run_resource_check(resource: Dict[str, Dict[str, str]]) -> None:
    """
    Checks basic information about the resource
    :param resource: current resource that is being prepared (dictionary loaded from yaml template file)
    """
    assert len(resource) == 1


def update_resource_with_defaults(
    resource: Dict[str, Dict[str, str]], resource_type: str
) -> Dict[str, Dict[str, str]]:
    """
    Extra process of updating resource dictionary with default values if possible (in case some of them were skipped),
        especially, creating a resource name for Terraform if wasn't specified
    :param resource: current resource that is being prepared (dictionary loaded from yaml template file)
    :param resource_type: name of the resource to create, e.g. aws_glue_crawler
    :return: resource dictionary with default values appended where possible
    """
    with open(f"./infra_defaults/{resource_type}.yaml") as f:
        resource_defaults = yaml.safe_load(f.read())
    for key in resource[resource_type].keys():
        resource_defaults.pop(key, None) if resource_defaults else None
    if resource_defaults:
        resource[resource_type].update(resource_defaults)

    # Creating a resource name for Terraform if wasn't specified
    if resource[resource_type].get("resource_name", None) is None:
        resource[resource_type]["resource_name"] = (
            resource_type + "_" + str(randint(10**4, 9 * 10**4))
        )

    return resource


def load_template(template_name: str) -> str:
    """
    Reads a template file from `infra_templates/` directory
    :param template_name: name of the template to load, e.g. aws_glue_crawler
    :return: string containing loaded template file
    """
    return open(f"infra_templates/{template_name}.tf").read()


def render_jinja(
    template: str,
    values_dict: Dict[str, str],
    jinja_environment: JinjaEnvironment,
) -> str:
    """
    If applicable, renders Jinja language inside a template file
    :param template: resource template file content read from `infra_templates/` directory
    :param values_dict: dictionary that contains values to be possibly filled inside Jinja template
    :param jinja_environment: Jinja Python framework environment to process template
    :return: resource in form of a simple string that should be forwarded to value filling process
    """
    jinja_template = jinja_environment.from_string(template)
    return jinja_template.render(values_dict)


def fill_template_values(
    resource: Dict[str, Dict[str, str]], resource_type: str, resource_template: str
) -> str:
    """
    Fills values inside a resource template file,
        in place of any param inside angle brackets: `<`, and `>`,
        fills value that is fetched either from provided config file (priority) or default values dictionary
    :param resource: current resource that is being prepared (dictionary loaded from yaml template file)
    :param resource_type: name of the resource to create, e.g. aws_glue_crawler
    :param resource_template: resource template file content read from `infra_templates/` directory,
        after Jinja processing if applicable
    :return: resource template with filled values. It shouldn't contain any angle bracket whatsoever after this step
    """
    for param, value in resource[resource_type].items():
        resource_template = resource_template.replace(f"<{param}>", str(value))

    return resource_template


def save_infra_setup_code(destination: str, output_main: str, env_main: str) -> None:
    """
    Saves infrastructure setup code into the specified location
    :param destination: where setup should be saved
    :param output_main: module main output string that contains whole Infrastructure as a Code setup,
    :param env_main: environment main output string that contains whole Infrastructure as a Code setup
        TODO: in future, divide it into main/variables/tfvars files, as well as separate modules
    """
    try:
        os.mkdir(destination)
        os.mkdir(f"{destination}/env")
        os.mkdir(f"{destination}/modules")
        os.mkdir(f"{destination}/modules/main")
    except OSError as error:
        logging.error(error)
        logging.info("Attempting to save infrastructure setup code in a given location")

    with open(f"{destination}/modules/main/main.tf", "w") as f:
        f.write(output_main)

    with open(f"{destination}/env/main.tf", "w") as f:
        f.write(env_main)
