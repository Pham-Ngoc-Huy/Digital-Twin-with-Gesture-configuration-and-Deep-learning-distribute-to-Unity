from abc import ABC, abstractmethod

class Stream(ABC):
    @abstractmethod
    def run(self):
        pass
