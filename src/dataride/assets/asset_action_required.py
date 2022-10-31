from typing import Dict
from dataclasses import dataclass

from jinja2 import Environment as JinjaEnvironment

from dataride.assets.asset import Asset
from dataride.utils.utils import log_if_verbose, render_jinja


@dataclass
class ActionRequired(Asset):
    """
    Extra asset class for Action Required documentation,
    that is created after infrastructure generation
    to enlist remaining necessary steps to have the data platform up and running.
    """

    def __init__(self, config: Dict, jinja_environment: JinjaEnvironment, verbose: bool):
        self.name = "action_required"
        self.config = config
        self.jinja_environment = jinja_environment
        self.verbose = verbose

    def save(self, destination: str) -> None:
        """
        Prepares action-required document for users after infrastructure generation

        :param destination: directory location for infrastructure setup generation
        """
        log_if_verbose("Preparing action_required.md file", self.verbose)

        with open(f"extra_assets/{self.name}/{self.name}.md") as f:
            action_required_rendered = render_jinja(f.read(), self.config, self.jinja_environment)

        with open(f"{destination}/{self.name}.md", "w") as f:
            f.write(action_required_rendered)
