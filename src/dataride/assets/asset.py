from typing import Dict
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod

from jinja2 import Environment as JinjaEnvironment


@dataclass
class Asset(metaclass=ABCMeta):
    """
    Abstract parent class for all extra assets possible to define
    """

    name: str
    config: Dict
    jinja_environment: JinjaEnvironment
    verbose: bool

    @abstractmethod
    def save(self, destination: str) -> None:
        raise NotImplementedError
