# plugins/base.py
class PluginBase(ABC):
    @abstractmethod
    def initialize(self, config: dict) -> None:
        pass
    
    @abstractmethod
    def get_commands(self) -> dict:
        pass

# plugins/zoom_control.py
class ZoomControlPlugin(PluginBase):
    def get_commands(self):
        return {
            "zoom_in": ["zoom in", "perbesar"],
            "zoom_out": ["zoom out", "perkecil"]
        }