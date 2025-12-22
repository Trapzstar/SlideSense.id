# recognizers/base.py
from abc import ABC, abstractmethod

class BaseVoiceRecognizer(ABC):
    @abstractmethod
    def listen(self) -> str:
        pass
    
    @abstractmethod
    def test_microphone(self) -> bool:
        pass