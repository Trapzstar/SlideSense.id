# config.py
class Config:
    # Voice recognition settings
    GOOGLE_LANGUAGE = "id-ID"
    FUZZY_THRESHOLD = 80
    PHONETIC_BONUS = 2
    
    # Timing settings
    COOLDOWN_SECONDS = 2
    LISTEN_TIMEOUT = 5
    PHRASE_LIMIT = 4
    
    # Audio settings
    DEFAULT_DEVICE = 1
    CALIBRATION_DURATION = 0.5
    
    # Debug settings
    DEBUG_MODE = True