import yaml
import logging
from random import randint
from typing import Dict, List

from jinja2 import Environment as JinjaEnvironment


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


def prepare_jinja_environment() -> JinjaEnvironment:
    """
    Prepares a Jinja environment for templates processing.
    Additionally, provides a helper function for raising errors while rendering templates

    :return: JinjaEnvironment object
    """

    def raise_helper(msg: str):
        """
        Function helping to raise an error in Jinja environment while rendering
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


def load_config(path: str) -> Dict:
    """
    Loads a YAML dataride config file into a Python dictionary

    :param path: where config file is stored
    :return: Python dictionary with loaded template resources
    """
    with open(path) as f:
        config = yaml.safe_load(f.read())

    return config


def load_template(template_name: str) -> str:
    """
    Loads a Terraform template file from `infra_templates/` directory

    :param template_name: name of the template to load, e.g. aws_glue_crawler
    :return: string containing loaded template file
    """
    return open(f"infra_templates/{template_name}.tf").read()


def update_resource_dict_with_defaults(
    resource_dict: Dict, resource_type: str, create_resource_name: bool = True
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
    values_dict: Dict,
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

    def map_single_value(par, val):
        """
        Supplementary internal function to easily map passed value to specific type of value digestible for Terraform

        :param par: parameter name to eventually raise error if value type is unknown
        :param val: value to map
        """
        if type(val) == bool or param == "type":
            return f"{str(val).lower()}"
        elif type(val) == str:
            if val.startswith("_"):
                return f"{str(val)[1:]}"
            else:
                return f'"{str(val)}"'
        elif type(val) == int or type(val) == float:
            return f"{str(val)}"
        elif type(val) == dict and val["is_variable"]:
            return f"var.{str(val['name'])}"
        else:
            raise ValueError(f"Wrong resource parameter value type for {par}")

    for param, value in values_dict.items():
        if type(value) == list:
            values_list_joined = ", ".join([map_single_value(param, elem) for elem in value])
            template = template.replace(f"<{param}>", f"[{values_list_joined}]")
        elif value is None:
            pass  # do nothing, but don't raise error
        else:
            template = template.replace(f"<{param}>", map_single_value(param, value))

    return template
