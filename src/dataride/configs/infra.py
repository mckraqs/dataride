import os
import logging
import subprocess
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

        self.__update_with_defaults()
        self.__check()

        self.config["resource_types"] = sorted(
            list(set([next(iter(resource)) for resource in self.config["resources"]]))
        )
        self.config["extra_asset_names"] = sorted(list(set([asset for asset in self.config["extra_assets"].keys()])))

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
        self.config["extra_assets"]["action_required"] = {}

        self.config["modules"] = {}

    def process_resources(self) -> None:
        # Clearing resources list to make the process idempotent
        self.resources = []

        for config_resource in self.config["resources"]:
            resource_name = next(iter(config_resource))
            resource = Resource(resource_name, config_resource[resource_name], self.jinja_environment, self.verbose)
            self.add_module_data(resource)
            self.resources.append(resource)

        self.update_config()

    def process_environments(self) -> None:
        # Clearing environments list to make the process idempotent
        self.environments = []

        for name_env, config_env in self.config["envs"].items():
            environment = Environment(name_env, config_env, self.jinja_environment, self.verbose)
            environment.extend_environment_data(self.config["providers"], self.modules)
            self.environments.append(environment)

        self.update_config()

    def process_modules(self) -> None:
        for module_name, module in self.modules.items():
            module.extend_module_data()

        self.update_config()

    def process_extra_assets(self) -> None:
        # Clearing assets list to make the process idempotent
        self.extra_assets = []

        for asset_name, asset_config in self.config["extra_assets"].items():
            if asset_config is None:
                asset_config = {}
            asset = ASSETS_DICT[asset_name]({**asset_config, **self.config}, self.jinja_environment, self.verbose)
            self.extra_assets.append(asset)

        self.update_config()

    def add_module_data(self, resource: Resource) -> None:
        """
        Fetch resource's information about module which it belongs
        :param resource: currently processed resource (dataride.configs.resource.Resource object)
        """
        if not self.modules.get(resource.module, False):
            self.modules[resource.module] = Module(resource.module, self.verbose)

        self.modules[resource.module].add_resource(resource)

    def update_config(self) -> None:
        self.config["resources"] = [{resource.name: resource.to_dict()} for resource in self.resources]

        for module_name, module in self.modules.items():
            self.config["modules"][module_name] = module.to_dict()

        for environment in self.environments:
            self.config["envs"][environment.name] = environment.to_dict()

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

        :param fmt: whether or not to format Terraform code
        """
        if fmt:
            log_if_verbose("Formatting Terraform code", self.verbose)
            subprocess.run(["terraform", "fmt", "-recursive", "-list=false", self.destination])

    def to_dict(self) -> Dict:
        return self.config
