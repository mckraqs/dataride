import os
import logging
import subprocess
from copy import deepcopy
from typing import List, Dict
from dataclasses import dataclass

from jinja2 import Environment as JinjaEnvironment

from dataride.utils.utils import update_resource_dict_with_defaults, log_if_verbose
from dataride.configs.elements import Module, Resource, Environment
from dataride.assets import Asset, ASSETS_DICT
from dataride.configs.abstracts import ToDict


@dataclass
class Infra(ToDict):
    """
    Class that holds overall infrastructure information of the whole data platform that is about to be generated
    """

    config: Dict
    destination: str
    resources: List[Resource]
    environments: List[Environment]
    modules: Dict[str, Module]
    extra_assets: List[Asset]
    verbose: bool

    def __init__(self, config_dict: Dict, destination: str, jinja_environment: JinjaEnvironment, verbose: bool):

        self.__default_name = "_config_infra"

        self.config = config_dict
        self.destination = destination
        self.resources = []
        self.environments = []
        self.modules = {}
        self.extra_assets = []
        self.jinja_environment = jinja_environment
        self.verbose = verbose

        self.__check()
        self.__update_with_defaults()

    def __check(self) -> None:
        log_if_verbose("\tRunning main config file check...", self.verbose)

        assert all(type(provider) == dict for provider in self.config["providers"])

        # Provider checks
        provider_names_list = []
        for provider in self.config["providers"]:
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

        log_if_verbose("\tConfig check passed!", self.verbose)

    def __update_with_defaults(self) -> None:
        update_resource_dict_with_defaults(self.config, self.__default_name, create_resource_name=False)

        if not self.config.get("resources", False):
            self.config["resources"] = []

        if not self.config.get("extra_assets", False):
            self.config["extra_assets"] = {}
        # To always make sure that action_required document is processed as the last extra asset
        self.config["extra_assets"]["action_required"] = self.config["extra_assets"].get("action_required", {})

        if not self.config.get("modules", False):
            self.config["modules"] = {}

    def __update_config(self, key: str) -> None:
        """
        Updates infrastructure config dictionary, based on a passed key
        TODO: When upgrading to Python 3.10, change this to match-case syntax
        :param key: key indicating which config part to update
        """
        if key == "resources":
            self.config["resources"] = [{resource.name: resource.to_dict()} for resource in self.resources]
            self.config["resource_types"] = sorted(
                list(set([next(iter(resource)) for resource in self.config["resources"]]))
            )
        elif key == "modules":
            for module_name, module in self.modules.items():
                self.config["modules"][module_name] = module.to_dict()
        elif key == "environments":
            for environment in self.environments:
                self.config["environments"][environment.name] = environment.to_dict()
        elif key == "extra_assets":
            self.config["extra_asset_names"] = sorted(
                list(set([asset for asset in self.config["extra_assets"].keys()]))
            )
        else:
            raise KeyError("Wrong key passed to update config dictionary")

    def __create_resources_from_configs(self, resources_configs: List[Dict], module_name: str = None) -> None:
        for resource_config in resources_configs:
            resource_name = next(iter(resource_config))

            # If module name is passed, resource's value should be overwritten
            if module_name is not None:
                if resource_config[resource_name] is None:
                    resource_config[resource_name] = {}  # creates a dictionary if resource_config is empty
                resource_config[resource_name]["_module"] = module_name

            resource = Resource(resource_name, resource_config[resource_name], self.jinja_environment, self.verbose)
            self.__create_module_if_not_existing(resource.module, {})
            self.modules[resource.module].add_resource(resource)
            self.resources.append(resource)

    def __create_module_if_not_existing(self, module_name: str, module_config: Dict) -> None:
        if not self.modules.get(module_name, False):
            self.modules[module_name] = Module(module_name, module_config, self.jinja_environment, self.verbose)

    def process_modules(self) -> None:
        """
        Iterates over modules passed in `modules` YAML config section, and initializes necessary objects.
        If applicable, creates all resources featured in a module's definition
        """
        for module_name, module_config in self.config["modules"].items():
            self.__create_module_if_not_existing(module_name, deepcopy(module_config))

            if module_config is not None and module_config.get("resources", False):
                self.__create_resources_from_configs(module_config["resources"], module_name)
            self.modules[module_name].extend_module_data()

        self.__update_config("modules")

    def process_resources(self) -> None:
        """
        Iterates over resources passed in `resources` YAML config section, and initializes necessary objects.
        """
        self.__create_resources_from_configs(self.config["resources"])
        self.__update_config("resources")
        self.__update_config("modules")

    def process_environments(self) -> None:
        """
        Iterates over environments passed in `environments` YAML config section, and initializes necessary objects.
        """
        for name_env, config_env in self.config["environments"].items():
            environment = Environment(name_env, config_env, self.jinja_environment, self.verbose)
            environment.extend_environment_data(self.config["providers"], self.modules)
            self.environments.append(environment)

        self.__update_config("environments")

    def process_extra_assets(self) -> None:
        """
        Iterates over extra assets passed in `extra_assets` YAML config section, and initializes necessary objects.
        """
        for asset_name, asset_config in self.config["extra_assets"].items():
            if asset_config is None:
                asset_config = {}
            asset = ASSETS_DICT[asset_name]({**asset_config, **self.config}, self.jinja_environment, self.verbose)
            self.extra_assets.append(asset)
            self.__update_config("extra_assets")

    def to_dict(self) -> Dict:
        return self.config

    def save(self) -> None:
        self.__save_structure()
        self.__save_modules()
        self.__save_environments()
        self.__save_extra_assets()

    def __save_structure(self) -> None:
        """
        Creates a result directory structure:
            - `destination` directory
            - Terraform modules directory
        If a `destination` directory exists, function breaks
        """
        log_if_verbose("Saving the infrastructure setup", self.verbose)

        try:
            os.mkdir(self.destination)
            os.mkdir(f"{self.destination}/modules")
        except OSError as error:
            logging.error(error)
            exit(1)

    def __save_modules(self) -> None:
        for module in self.modules.values():
            module.save(self.destination)

    def __save_environments(self) -> None:
        for environment in self.environments:
            environment.save(self.destination)

    def __save_extra_assets(self) -> None:
        for asset in self.extra_assets:
            asset.save(self.destination)

    def format_code(self, fmt: bool) -> None:
        """
        If applicable, formats generated code. So far only `Terraform fmt` function call is available

        :param fmt: whether to format Terraform code
        """
        if fmt:
            log_if_verbose("Formatting Terraform code", self.verbose)
            subprocess.run(["terraform", "fmt", "-recursive", "-list=false", self.destination])
