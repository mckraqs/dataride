import os
import logging
from typing import Dict, List
from dataclasses import dataclass

from dataride.configs.elements.variable import Variable
from dataride.utils.utils import log_if_verbose
from dataride.configs.abstracts import ToDict


@dataclass
class Module(ToDict):
    """
    Class that holds information about a particular Terraform module created
        as a result of infrastructure generation with `dataride` package.
    """

    name: str
    main_tf: str
    var_tf: str
    vars_with_def: List[Variable]
    vars_no_def: List[Variable]
    verbose: bool

    def __init__(self, name, verbose):
        self.name = name
        self.main_tf = ""
        self.var_tf = ""
        self.vars_with_def = []
        self.vars_no_def = []
        self.verbose = verbose

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "main_tf": self.main_tf,
            "var_tf": self.var_tf,
            "vars_with_def": [var.name for var in self.vars_with_def],
            "vars_no_def": [var.name for var in self.vars_no_def],
        }

    def save(self, destination: str) -> None:
        """
        Saves infrastructure module setup code into the specified location
        If a `module` directory exists, function breaks
        :param destination: directory location for infrastructure setup generation
        :param verbose: whether to print more outputs
        """
        log_if_verbose(f"\tSaving module: {self.name}...", self.verbose)

        try:
            os.mkdir(f"{destination}/modules/{self.name}")
        except OSError as error:
            logging.error(error)
            exit(1)

        with open(f"{destination}/modules/{self.name}/main.tf", "w") as f:
            f.write(self.main_tf)

        # it may happen that module doesn't have any variables
        if self.var_tf:
            with open(f"{destination}/modules/{self.name}/var.tf", "w") as f:
                f.write(self.var_tf)

        log_if_verbose(f"\tModule saved!", self.verbose)
