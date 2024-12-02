from abc import ABC, abstractmethod

class DiagnosticAnalysis(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def collect():
        pass

    @abstractmethod
    def perform():
        pass

    @abstractmethod
    def report():
        pass
