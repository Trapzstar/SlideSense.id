class SmartVoiceDetector:
    def __init__(self):
        self._fuzzy_available = None
        self._phonetic_available = None
        
    @property
    def fuzzy_available(self):
        if self._fuzzy_available is None:
            try:
                import fuzzywuzzy
                self._fuzzy_available = True
            except ImportError:
                self._fuzzy_available = False
        return self._fuzzy_available