from typing import Dict, List, Union
from dataclasses import dataclass

from jinja2 import Environment as JinjaEnvironment

from dataride.utils.utils import (
    update_resource_dict_with_defaults,
    log_if_verbose,
    load_template,
    render_jinja,
    fetch_resource_variables,
    fill_template_values,
)


@dataclass
class Resource:
    """
    Class that holds information about a particular Terraform resource created
        as a result of infrastructure generation with `dataride` package.
    """

    name: str
    config: Dict[str, str]
    module: str
    template: str
    template_filled: str
    variables: Dict[str, Union[str, List[str]]]
    jinja_environment: JinjaEnvironment
    verbose: bool

    def __init__(self, name, config_dict, jinja_environment, verbose):

        self.name = name
        self.config = config_dict[self.name]
        self.verbose = verbose
        self.jinja_environment = jinja_environment

        self.__check()
        self.__update_with_defaults()

        self.module = self.config["_module"]
        self.variables = self.__get_variables()
        self.template = load_template(self.name)
        self.__render_template()
        self.template_filled = fill_template_values(self.template, self.config)

        self.log_stats()

    def __check(self) -> None:
        """
        Checks basic information about the resource.
        """
        log_if_verbose(f"\tRunning resource config check for {self.name}...", self.verbose)

        assert len(self.config) > 0

        log_if_verbose("\tResource config check passed!", self.verbose)

    def __update_with_defaults(self):
        self.config = update_resource_dict_with_defaults(self.config, self.name)

    def __render_template(self):
        if self.config["_jinja"]:
            self.template = render_jinja(self.template, self.config, self.jinja_environment)

    def __get_variables(self):
        return fetch_resource_variables(self.config, self.jinja_environment)

    def log_stats(self):
        log_if_verbose(
            f"\tResource ({self.name}) variables: with default values - {len(self.variables['vars_with_def'])},"
            f" no default values - {len(self.variables['vars_no_def'])}",
            self.verbose,
        )
