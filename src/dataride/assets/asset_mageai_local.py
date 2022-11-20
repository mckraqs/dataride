from typing import Dict
from dataclasses import dataclass
from distutils.dir_util import copy_tree

from jinja2 import Environment as JinjaEnvironment

from dataride.assets.asset import Asset
from dataride.utils.utils import log_if_verbose


@dataclass
class MageAILocal(Asset):
    def __init__(self, config: Dict, jinja_environment: JinjaEnvironment, verbose: bool):
        self.name = "mageai_local"
        self.config = config
        self.jinja_environment = jinja_environment
        self.verbose = verbose

    def save(self, destination: str) -> None:
        """
        Prepares `mage-ai` local environment extra asset attached to the generated infrastructure

        :param destination: directory location for infrastructure setup generation
        """
        log_if_verbose("Preparing mage-ai local environment", self.verbose)

        copy_tree(f"extra_assets/{self.name}", f"{destination}/{self.name}")
