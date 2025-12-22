# recognizer_factory.py
class RecognizerFactory:
    @staticmethod
    def create_recognizer(type_: str) -> BaseVoiceRecognizer:
        if type_ == "google":
            return GoogleVoiceRecognizer()
        elif type_ == "offline":
            return OfflineVoiceRecognizer()
        elif type_ == "hybrid":
            return HybridVoiceRecognizer()
        else:
            raise ValueError(f"Unknown recognizer type: {type_}")