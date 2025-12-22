from functools import lru_cache

class SmartVoiceDetector:
    @lru_cache(maxsize=100)
    def calculate_similarity(self, text1: str, text2: str) -> float:
        # Cache similarity calculations
        return fuzz.ratio(text1, text2)