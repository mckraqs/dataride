from typing import Dict, List

from jinja2 import Environment as JinjaEnvironment

from dataride.configs.elements.variable import Variable


def fetch_resource_variables(resource_dict: Dict, jinja_environment: JinjaEnvironment, verbose: bool) -> List:
    """
    TODO: create a description here

    :param resource_dict:
    :param jinja_environment:
    :param verbose:
    :return:
    """
    variables = []

    for field_name, field_value in resource_dict.items():
        if type(field_value) == dict and field_value.get("is_variable", False):
            var = Variable(field_name, field_value, jinja_environment, verbose)
            variables.append(var)

    return variables
