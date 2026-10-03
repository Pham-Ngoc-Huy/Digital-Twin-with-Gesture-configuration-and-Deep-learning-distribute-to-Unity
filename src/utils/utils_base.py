import numpy as np
from abc import ABC, abstractmethod

class Utils(ABC):
    @abstractmethod
    def process(self):
        pass