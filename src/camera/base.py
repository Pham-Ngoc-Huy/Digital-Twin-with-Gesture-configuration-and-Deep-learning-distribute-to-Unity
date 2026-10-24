from abc import ABC, abstractmethod

class Stream(ABC):
    @abstractmethod
    def turn_cam(self):
        pass

    @abstractmethod
    def plot_marker(self):
        pass