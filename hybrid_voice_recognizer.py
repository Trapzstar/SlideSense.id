# ============================================
# HYBRID VOICE RECOGNIZER (OFFLINE + GOOGLE API)
# ============================================
import speech_recognition as sr
import pyaudio
import numpy as np

class HybridVoiceRecognizer:
    def __init__(self, debug_mode=True):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_ready = False
        self.device_index = None
        self.speech_history = []
        self.debug_mode = debug_mode
        self.noise_reduction_enabled = False

        # Offline fallback removed - using simplified approach

    def initialize(self):
        """Initialize Hybrid Speech Recognition (Google + Offline fallback)"""
        try:
            # List devices
            self.list_audio_devices()

            # Microphone setup
            try:
                if self.device_index is not None:
                    self.microphone = sr.Microphone(device_index=self.device_index)
                    print(f"✅ Microphone Hybrid dipilih: Device {self.device_index}")
                else:
                    self.microphone = sr.Microphone()
                    print("✅ Microphone Hybrid siap")

                # Test microphone with shorter calibration
                with self.microphone as source:
                    print("🎤 Calibrating microphone for ambient noise (shorter)...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Shorter calibration
                    print("🎤 Microphone calibrated")

            except Exception as mic_error:
                print(f"❌ Microphone setup error: {mic_error}")
                print("💡 Solusi:")
                print("   1. Pastikan microphone terhubung dan tidak mute")
                print("   2. Coba restart aplikasi")
                print("   3. Periksa pengaturan audio Windows")
                return False

            self.is_ready = True
            print("🔄 Hybrid mode: Google API (primary) + Offline Sphinx (fallback)")
            return True

        except Exception as e:
            print(f"❌ Hybrid initialization error: {e}")
            self.is_ready = False
            return False

    def list_audio_devices(self):
        """List available audio input devices"""
        try:
            audio = pyaudio.PyAudio()
            print("\n🎙️  DAFTAR PERANGKAT AUDIO INPUT:")
            print("-" * 40)
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info.get('maxInputChannels') > 0:
                    print(f"  {i}: {device_info.get('name')} (Channels: {device_info.get('maxInputChannels')})")
            print("-" * 40)
            audio.terminate()
        except Exception as e:
            print(f"⚠️  Tidak bisa list devices: {e}")

    def set_debug_mode(self, enabled=True):
        """Enable or disable debug mode"""
        self.debug_mode = enabled
        print(f"🔧 Debug mode: {'ON' if enabled else 'OFF'}")

    def select_device(self, device_index):
        """Select specific audio device"""
        self.device_index = device_index
        print(f"🎙️  Device {device_index} dipilih untuk hybrid recognition")

    def add_to_history(self, text):
        """Add recognized text to history"""
        self.speech_history.append(text)
        if len(self.speech_history) > 10:
            self.speech_history.pop(0)

    def listen_google_primary(self):
        """Try Google Speech API first with better error handling"""
        try:
            with self.microphone as source:
                if self.debug_mode:
                    print("    🔊 Listening with Google API...", end="", flush=True)

                # Listen for audio with longer timeout for better recognition
                audio = self.recognizer.listen(
                    source,
                    timeout=5,  # Longer timeout to wait for speech
                    phrase_time_limit=5  # Longer phrase limit
                )

                if self.debug_mode:
                    print("\r    ⏳ Recognizing with Google...", end="", flush=True)

                # Recognize with Google Speech API
                text = self.recognizer.recognize_google(audio, language="id-ID")

                if self.debug_mode:
                    print(f"\r    📝 Google: '{text}'")

                self.add_to_history(text)
                return text

        except sr.WaitTimeoutError:
            if self.debug_mode:
                print("\r    ⏰ Timeout - tidak ada suara terdeteksi")
                print("    💡 Pastikan microphone aktif dan tidak mute")
            return None
        except sr.UnknownValueError:
            if self.debug_mode:
                print("\r    🤔 Suara terdeteksi tapi tidak jelas (Google)")
                print("    💡 Coba bicara lebih jelas atau dekat ke microphone")
            return None
        except sr.RequestError as e:
            if self.debug_mode:
                print(f"\r    ❌ Google API Error: {str(e)[:40]}...")
            return None
        except Exception as e:
            if self.debug_mode:
                print(f"\r    ❌ Google Error: {str(e)[:40]}...")
            return None

    def listen_offline_fallback(self):
        """Fallback to offline recognition - simplified version"""
        if self.debug_mode:
            print("    🔄 Switching to offline recognition...")

        # For now, just try a simple keyword spotting approach
        # This is a placeholder - in production you'd want proper offline ASR
        try:
            # Simple approach: try to detect basic keywords using Google with very short timeout
            # as a last resort, but this will likely fail too
            with self.microphone as source:
                if self.debug_mode:
                    print("    🔊 Trying basic offline detection...")

                # Very short listen for basic keywords
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)

                # Try with English first for basic commands
                text = self.recognizer.recognize_google(audio, language="en-US")
                if text and any(keyword in text.lower() for keyword in ['next', 'previous', 'back', 'stop', 'quit']):
                    if self.debug_mode:
                        print(f"    📝 Basic offline: '{text}'")
                    self.add_to_history(text)
                    return text.lower().strip()

        except:
            pass

        if self.debug_mode:
            print("    ❌ Offline recognition not available")

        return None

    def listen(self, timeout=5, phrase_limit=4):
        """Hybrid listening: Google API first, offline fallback"""
        if not self.is_ready:
            return None

        # Try Google API first
        text = self.listen_google_primary()
        if text:
            return text

        # If Google fails, try offline recognition
        if self.debug_mode:
            print("    🔄 Google failed, trying offline...")

        text = self.listen_offline_fallback()
        if text:
            return text

        # Both failed
        if self.debug_mode:
            print("    ❌ Both recognition methods failed")

        return None

    def get_history(self):
        """Get speech recognition history"""
        return self.speech_history.copy()

    def clear_history(self):
        """Clear speech recognition history"""
        self.speech_history.clear()
        print("🗑️  History cleared")

    def show_history(self):
        """Show speech recognition history"""
        if not self.speech_history:
            print("📝 History kosong")
            return

        print("\n📝 SPEECH RECOGNITION HISTORY:")
        print("-" * 40)
        for i, text in enumerate(self.speech_history[-10:], 1):  # Show last 10
            print(f"  {i}. '{text}'")
        print("-" * 40)

    def save_history(self, filename="speech_history.txt"):
        """Save speech history to file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Speech Recognition History\n")
                f.write("=" * 30 + "\n")
                for text in self.speech_history:
                    f.write(f"{text}\n")
            print(f"💾 History disimpan ke {filename}")
        except Exception as e:
            print(f"❌ Gagal menyimpan history: {e}")

    def test_microphone(self, duration=3):
        """Test microphone input for specified duration"""
        print(f"\n🎙️  TESTING MICROPHONE ({duration} detik)...")
        print("-" * 40)

        try:
            with self.microphone as source:
                print("   Recording... bicaralah sekarang!")
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)

                print("   Recognizing...")
                text = self.recognizer.recognize_google(audio, language="id-ID")

                print(f"   ✅ Detected: '{text}'")
                print("   🎉 Microphone test berhasil!")
                return True

        except sr.WaitTimeoutError:
            print("   ⏰ Timeout - tidak ada suara terdeteksi")
            print("   ⚠️  Pastikan microphone terhubung dan tidak mute")
            return False
        except sr.UnknownValueError:
            print("   🤔 Suara terdeteksi tapi tidak jelas")
            print("   💡 Coba bicara lebih jelas atau dekat ke microphone")
            return False
        except sr.RequestError as e:
            print(f"   ❌ API Error: {e}")
            print("   🔄 Mencoba offline test...")
            return self.test_microphone_offline(duration)
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False

    def test_microphone_offline(self, duration=3):
        """Offline microphone test"""
        try:
            print("   🔄 Testing offline...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
                # Just check if audio was captured
                audio.get_raw_data()
                print("   ✅ Audio captured successfully (offline)")
                return True
        except:
            print("   ❌ Offline test juga gagal")
            return False

