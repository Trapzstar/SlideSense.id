# commands/base.py
from abc import ABC, abstractmethod

class PowerPointCommand(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass

# commands/next_slide.py
class NextSlideCommand(PowerPointCommand):
    def execute(self) -> str:
        pyautogui.press('right')
        return "✅ SLIDE MAJU!"