import os
import logging
from typing import Dict, List, Union
from dataclasses import dataclass, asdict

from jinja2 import Environment as JinjaEnvironment

from dataride.utils.utils import (
    load_template,
    update_resource_dict_with_defaults,
    fetch_resource_variables,
    render_jinja,
    log_if_verbose,
)


@dataclass
class Environment:
    """
    Class that holds information about a particular Terraform environment created
        as a result of infrastructure generation with `dataride` package.
    """

    name: str
    config: Dict[str, str]
    main_tf: str
    var_tf: str
    template: str
    variables: Dict[str, Union[str, List[str]]]
    jinja_environment: JinjaEnvironment
    verbose: bool

    def __init__(self, name: str, config_dict: Dict[str, str], jinja_environment: JinjaEnvironment, verbose: bool):

        self.__default_name = "_config_environment"

        self.name = name
        self.config = config_dict
        self.main_tf = ""
        self.var_tf = ""
        self.jinja_environment = jinja_environment
        self.verbose = verbose

        self.__check()
        self.__update_with_defaults()

        self.variables = self.__get_variables()
        self.template = load_template("env_default")

    def __check(self):
        pass

    def __get_variables(self):
        return fetch_resource_variables(self.config, self.jinja_environment)

    def __update_with_defaults(self):
        if self.config is None:
            self.config = {}

        self.config = update_resource_dict_with_defaults(self.config, self.__default_name, create_resource_name=False)

    def extend_environment_data(self, infra_providers, infra_modules):
        """
        Extends environment's information with proper `main_tf` and `var_tf` values
        :param infra_providers: list of infrastructure's providers, passed from the main Infra objects
        :param infra_modules: dictionary of infrastructure's modules, passed from the main Infra objects
        """
        self.var_tf = self.variables["result_str"]

        infra_modules_transformed = {name: asdict(config) for name, config in infra_modules.items()}
        full_template_config = {
            "modules": infra_modules_transformed,
            "providers": infra_providers,
            **{"env": {**self.config}},
        }
        self.main_tf = render_jinja(self.template, full_template_config, self.jinja_environment)

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

    def log_stats(self):
        log_if_verbose(
            f"\tEnvironment ({self.name}) variables: with default values - {len(self.variables['vars_with_def'])},"
            f" no default values - {len(self.variables['vars_no_def'])}",
            self.verbose,
        )
