from abc import ABC, abstractmethod


class BaseModel(ABC):

    @abstractmethod
    def eval(self):
        pass

    @abstractmethod
    def serve(self, port):
        pass

    @abstractmethod
    def test(self):
        pass

    @abstractmethod
    def package(self, platform):
        pass
