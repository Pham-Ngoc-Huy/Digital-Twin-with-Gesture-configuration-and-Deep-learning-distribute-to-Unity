from abc import ABC, abstractmethod

class TestCases(ABC):
    @abstractmethod
    def test_run(self):
        pass