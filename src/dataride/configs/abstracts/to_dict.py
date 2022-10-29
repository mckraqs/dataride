from typing import Dict
from abc import ABCMeta, abstractmethod


class ToDict(metaclass=ABCMeta):
    @abstractmethod
    def to_dict(self) -> Dict:
        raise NotImplementedError
