from typing import Union, Dict
from dataclasses import dataclass

from jinja2 import Environment as JinjaEnvironment

from dataride.utils import load_template, update_resource_dict_with_defaults, render_jinja, fill_template_values
from dataride.configs.abstracts import ToDict


@dataclass
class Variable(ToDict):
    """
    Class that holds information about one specific Terraform variable
    """

    target: str
    name: str
    type: str
    default_value: Union[str, bool, int, float]
    description: str
    config: Dict
    template: str
    template_filled: str
    jinja_environment: JinjaEnvironment
    verbose: bool

    def __init__(self, target: str, config_dict: Dict, jinja_environment: JinjaEnvironment, verbose: bool):
        self.__default_name = "_config_variable"

        self.target = target
        self.config = config_dict
        self.jinja_environment = jinja_environment
        self.verbose = verbose

        self.__check()
        self.__update_with_defaults()
        self.__fetch_params_values()

        self.template = render_jinja(load_template(self.__default_name), self.config, self.jinja_environment)
        self.template_filled = fill_template_values(self.template, self.config)

    def __str__(self):
        return self.template_filled

    def __check(self) -> None:
        assert self.config.get("type", False)

    def __update_with_defaults(self) -> None:
        self.config = update_resource_dict_with_defaults(self.config, self.__default_name, create_resource_name=False)
        self.config["target"] = self.target
        if self.config.get("name", False):
            self.name = self.config["name"]
        else:
            self.name = self.target
            self.config["name"] = self.name

    def __fetch_params_values(self) -> None:
        self.type = self.config["type"]
        self.default_value = self.config["default_value"]
        self.description = self.config["description"]

    def to_dict(self) -> Dict:
        return self.config
