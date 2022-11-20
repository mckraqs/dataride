import os
import logging
from typing import Dict, List
from dataclasses import dataclass

from jinja2 import Environment as JinjaEnvironment

from dataride.utils import (
    load_template,
    update_resource_dict_with_defaults,
    render_jinja,
    log_if_verbose,
)
from dataride.configs.elements.variable import Variable
from dataride.configs.elements.module import Module
from dataride.configs.abstracts import ToDict


@dataclass
class Environment(ToDict):
    """
    Class that holds information about a particular Terraform environment created
        as a result of infrastructure generation with `dataride` package.
    """

    name: str
    config: Dict
    main_tf: str
    var_tf: str
    template: str
    variables: List[Variable]
    variables_names: List[str]
    jinja_environment: JinjaEnvironment
    verbose: bool

    def __init__(self, name: str, config_dict: Dict[str, str], jinja_environment: JinjaEnvironment, verbose: bool):

        self.__default_name = "_config_environment"

        self.name = name
        self.config = config_dict
        self.main_tf = ""
        self.var_tf = ""
        self.variables = []
        self.jinja_environment = jinja_environment
        self.verbose = verbose

        self.__check()
        self.__update_with_defaults()
        self.__get_variables()
        self.template = load_template(self.__default_name)

        self.__update_config()

    def __check(self) -> None:
        pass

    def __update_with_defaults(self) -> None:
        if self.config is None:
            self.config = {}

        self.config = update_resource_dict_with_defaults(self.config, self.__default_name, create_resource_name=False)

    def __update_config(self) -> None:
        self.config["name"] = self.name
        self.config["main.tf"] = self.main_tf
        self.config["var.tf"] = self.var_tf
        self.config["variables_names"] = self.variables_names
        for var in self.variables:
            self.config["variables"].update({var.target: var.to_dict()})

    def __get_variables(self) -> None:
        if self.config.get("variables", False):
            for var_name, var_config in self.config["variables"].items():
                var = Variable(var_name, var_config, self.jinja_environment, self.verbose)
                self.variables.append(var)

        self.variables_names = [var.name for var in self.variables]

    def extend_environment_data(self, infra_providers: Dict, infra_modules: Dict[str, Module]) -> None:
        """
        Extends environment's information with proper `main_tf` and `var_tf` values

        :param infra_providers: list of infrastructure's providers, passed from the main Infra objects
        :param infra_modules: dictionary of infrastructure's modules, passed from the main Infra objects
        """
        self.var_tf = "\n\n".join([str(var) for var in self.variables])
        infra_modules_transformed = {module_name: module.to_dict() for module_name, module in infra_modules.items()}
        full_template_config = {
            "modules": infra_modules_transformed,
            "providers": infra_providers,
            "env": {**self.config},
        }
        self.main_tf = render_jinja(self.template, full_template_config, self.jinja_environment)

        self.__update_config()

    def to_dict(self) -> Dict:
        return self.config

    def save(self, destination: str) -> None:
        """
        Saves infrastructure environment setup code into the specified location
        If an environment directory exists, function breaks

        :param destination: directory location for infrastructure setup generation
        """
        log_if_verbose(f"\tSaving environment: {self.name}...", self.verbose)

        try:
            os.mkdir(f"{destination}/{self.name}")
        except OSError as error:
            logging.error(error)
            exit(1)

        with open(f"{destination}/{self.name}/main.tf", "w") as f:
            f.write(self.main_tf)

        # it may happen that environment doesn't have any variables
        if self.var_tf:
            with open(f"{destination}/{self.name}/var.tf", "w") as f:
                f.write(self.var_tf)

        log_if_verbose(f"\tEnvironment saved!", self.verbose)

    def log_stats(self) -> None:
        vars_with_def = [var for var in self.variables if var.default_value is not None]
        vars_no_def = [var for var in self.variables if var.default_value is None]
        log_if_verbose(
            f"\tEnvironment ({self.name}) variables: with default values - {len(vars_with_def)},"
            f" no default values - {len(vars_no_def)}",
            self.verbose,
        )
