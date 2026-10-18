from abc import ABC, abstractmethod

class Kinematics(ABC):
    def __init__(
        self,   
        base_vec: list,
        ref_vec: list
    ):
        self.base_vec = base_vec
        self.ref_vec = ref_vec

    @abstractmethod
    def process(self):
        pass