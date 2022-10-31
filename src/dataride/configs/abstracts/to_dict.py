from typing import Dict
from abc import ABCMeta, abstractmethod


class ToDict(metaclass=ABCMeta):
    """
    Interface that indicates that a child class can be converted to the dictionary
    (usable for Terraform elements classes)
    """

    @abstractmethod
    def to_dict(self) -> Dict:
        raise NotImplementedError
