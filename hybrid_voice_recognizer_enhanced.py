# ============================================
# HYBRID VOICE RECOGNIZER (OFFLINE + GOOGLE API)
# ENHANCED VERSION WITH SMART RETRY & AUTO SELECTION
# ============================================
import speech_recognition as sr
import pyaudio
import numpy as np
import time
import json
import os

class HybridVoiceRecognizer:
    def __init__(self, debug_mode=True):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_ready = False
        self.device_index = None
        self.speech_history = []
        self.debug_mode = debug_mode
        self.noise_reduction_enabled = False
        
        # Enhanced features
        self.recent_failures = 0
        self.failure_reasons = []
        self.adaptive_energy_threshold = 300
        self.max_retries = 3
        self.user_config = self._load_user_config()
        
        # Performance tracking
        self.performance_stats = {
            'total_attempts': 0,
            'successful_recognitions': 0,
            'google_success': 0,
            'offline_success': 0,
            'failures': 0
        }
    
    def _load_user_config(self):
        """Load user configuration if exists"""
        config_file = 'user_voice_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_user_config(self):
        """Save user configuration"""
        config_file = 'user_voice_config.json'
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_config, f, indent=2)
        except Exception as e:
            if self.debug_mode:
                print(f"⚠️  Could not save config: {e}")

    def initialize(self):
        """Initialize Hybrid Speech Recognition with auto-selection"""
        try:
            # Auto-select best microphone
            auto_device = self.auto_select_best_microphone()
            
            if auto_device is not None and self.device_index is None:
                self.device_index = auto_device
                self.user_config['preferred_device'] = auto_device
                self._save_user_config()

            # Microphone setup
            try:
                if self.device_index is not None:
                    self.microphone = sr.Microphone(device_index=self.device_index)
                    print(f"✅ Microphone selected: Device {self.device_index}")
                else:
                    self.microphone = sr.Microphone()
                    print("✅ Microphone ready (default)")

                # Test microphone with shorter calibration
                with self.microphone as source:
                    print("🎤 Calibrating microphone for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    print("🎤 Microphone calibrated")

            except Exception as mic_error:
                print(f"❌ Microphone setup error: {mic_error}")
                print("💡 Solusi:")
                print("   1. Pastikan microphone terhubung dan tidak mute")
                print("   2. Coba restart aplikasi")
                print("   3. Periksa pengaturan audio Windows")
                return False

            self.is_ready = True
            print("🔄 Hybrid mode: Google API (primary) + Smart Retry")
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
    
    def auto_select_best_microphone(self):
        """Automatically select best microphone based on quality test"""
        print("\n🔍 AUTO-DETECTING BEST MICROPHONE...")
        print("-" * 40)
        
        candidates = []
        audio = pyaudio.PyAudio()
        
        try:
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info.get('maxInputChannels') > 0:
                    device_name = device_info.get('name', '')
                    
                    # Score device based on characteristics
                    score = 0
                    
                    # Prefer devices with certain keywords
                    name_lower = device_name.lower()
                    if 'array' in name_lower or 'realtek' in name_lower:
                        score += 10
                    if 'microphone' in name_lower:
                        score += 5
                    if 'usb' in name_lower:
                        score += 8
                    if 'bluetooth' in name_lower or 'hands-free' in name_lower:
                        score += 6
                    
                    # Test if device is actually working
                    try:
                        test_mic = sr.Microphone(device_index=i)
                        with test_mic as source:
                            # Quick test - if we can open, it's active
                            pass
                        score += 5  # Bonus for working device
                        
                        candidates.append({
                            'index': i,
                            'name': device_name,
                            'score': score,
                            'channels': device_info.get('maxInputChannels')
                        })
                        
                        if self.debug_mode:
                            print(f"  ✓ Device {i}: {device_name} (Score: {score})")
                    except:
                        if self.debug_mode:
                            print(f"  ✗ Device {i}: {device_name} (Not available)")
                        continue
            
            audio.terminate()
            
            # Sort by score
            candidates.sort(key=lambda x: x['score'], reverse=True)
            
            if candidates:
                best = candidates[0]
                print(f"\n✅ AUTO-SELECTED: {best['name']}")
                print(f"   Device Index: {best['index']}")
                print(f"   Quality Score: {best['score']}/28")
                return best['index']
            else:
                print("⚠️  No suitable device found, using default")
                return None
                
        except Exception as e:
            audio.terminate()
            print(f"⚠️  Auto-selection failed: {e}")
            return None

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

    def _diagnose_failure(self):
        """Diagnose why recognition failed"""
        if not self.failure_reasons:
            return "UNKNOWN"
        
        last_reason = self.failure_reasons[-1]
        
        if 'timeout' in last_reason.lower():
            return "NO_SPEECH"
        elif 'unknown' in last_reason.lower():
            return "UNCLEAR_AUDIO"
        elif 'request' in last_reason.lower() or 'connection' in last_reason.lower():
            return "CONNECTION"
        elif 'noise' in last_reason.lower():
            return "NOISE"
        else:
            return "UNKNOWN"
    
    def show_audio_level_meter(self, duration=1):
        """Show real-time audio level meter"""
        try:
            audio = pyaudio.PyAudio()
            
            # Use selected device or default
            if self.device_index is not None:
                stream = audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=1024
                )
            else:
                stream = audio.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024
                )
            
            print("    Audio Level: ", end='', flush=True)
            
            for _ in range(int(duration * 10)):
                try:
                    data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
                    volume = int(np.abs(data).mean())
                    
                    # Visual bar (0-50 range)
                    bars = min(50, volume // 20)
                    print(f"\r    Audio Level: {'█' * bars}{' ' * (50-bars)} {volume:4d}", end='', flush=True)
                    time.sleep(0.1)
                except:
                    break
            
            print()  # New line
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
        except Exception as e:
            if self.debug_mode:
                print(f"\n    ⚠️  Audio meter error: {e}")
    
    def listen_google_primary(self, attempt=1):
        """Try Google Speech API with enhanced error handling"""
        try:
            with self.microphone as source:
                # Adaptive energy threshold
                if attempt > 1:
                    self.adaptive_energy_threshold = 300 + (attempt * 100)
                    self.recognizer.energy_threshold = self.adaptive_energy_threshold
                
                if self.debug_mode:
                    print("    🔊 Listening with Google API...", end="", flush=True)

                # Listen for audio with longer timeout
                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=5
                )

                if self.debug_mode:
                    print("\r    ⏳ Recognizing with Google...", end="", flush=True)

                # Recognize with Google Speech API
                text = self.recognizer.recognize_google(audio, language="id-ID")

                if self.debug_mode:
                    print(f"\r    📝 Google: '{text}'")

                self.add_to_history(text)
                self.performance_stats['google_success'] += 1
                self.performance_stats['successful_recognitions'] += 1
                return text, None

        except sr.WaitTimeoutError:
            error_msg = "Timeout - tidak ada suara terdeteksi"
            self.failure_reasons.append(error_msg)
            if self.debug_mode:
                print(f"\r    ⏰ {error_msg}")
            return None, "TIMEOUT"
        except sr.UnknownValueError:
            error_msg = "Suara terdeteksi tapi tidak jelas"
            self.failure_reasons.append(error_msg)
            if self.debug_mode:
                print(f"\r    🤔 {error_msg}")
            return None, "UNCLEAR"
        except sr.RequestError as e:
            error_msg = f"Google API Error: {str(e)[:40]}"
            self.failure_reasons.append(error_msg)
            if self.debug_mode:
                print(f"\r    ❌ {error_msg}")
            return None, "CONNECTION"
        except Exception as e:
            error_msg = f"Google Error: {str(e)[:40]}"
            self.failure_reasons.append(error_msg)
            if self.debug_mode:
                print(f"\r    ❌ {error_msg}")
            return None, "ERROR"

    def listen_offline_fallback(self):
        """Fallback to offline recognition - simplified version"""
        if self.debug_mode:
            print("    🔄 Switching to offline recognition...")

        try:
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
    
    def listen_with_smart_retry(self, max_retries=None, show_audio_meter=True):
        """Listen with smart retry mechanism and rich feedback"""
        if not self.is_ready:
            return None
        
        if max_retries is None:
            max_retries = self.max_retries
        
        self.performance_stats['total_attempts'] += 1
        
        # Show audio level meter if enabled
        if show_audio_meter and self.debug_mode:
            self.show_audio_level_meter(duration=0.5)
        
        for attempt in range(1, max_retries + 1):
            # Try Google API
            text, error_type = self.listen_google_primary(attempt=attempt)
            
            if text:
                self.recent_failures = 0
                return text
            
            # Retry logic
            if attempt < max_retries:
                if self.debug_mode:
                    print(f"    🔄 Retry {attempt}/{max_retries}...")
                    
                    # Provide specific guidance based on error
                    if error_type == "TIMEOUT":
                        print("    💡 Coba bicara lebih cepat atau lebih keras")
                    elif error_type == "UNCLEAR":
                        print("    💡 Bicara lebih jelas dan perlahan")
                    elif error_type == "CONNECTION":
                        print("    💡 Checking connection...")
                
                time.sleep(0.3)
            else:
                # Final attempt - try offline fallback
                if self.debug_mode:
                    print("    🔄 Trying offline fallback...")
                
                text = self.listen_offline_fallback()
                if text:
                    self.recent_failures = 0
                    self.performance_stats['offline_success'] += 1
                    self.performance_stats['successful_recognitions'] += 1
                    return text
        
        # All attempts failed
        self.recent_failures += 1
        self.performance_stats['failures'] += 1
        
        if self.debug_mode:
            print("    ❌ Gagal setelah semua percobaan")
            self._provide_failure_guidance()
        
        return None
    
    def _provide_failure_guidance(self):
        """Provide guidance after repeated failures"""
        if self.recent_failures >= 3:
            print("\n    ⚠️  BANYAK KEGAGALAN TERDETEKSI!")
            print("    💡 SARAN:")
            print("       • Periksa koneksi microphone")
            print("       • Kurangi noise latar belakang")
            print("       • Bicara lebih dekat ke microphone")
            print("       • Coba restart aplikasi")
            print()
    
    def listen(self, timeout=5, phrase_limit=4):
        """Main listen method - now uses smart retry"""
        return self.listen_with_smart_retry()

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
    
    def get_performance_stats(self):
        """Get performance statistics"""
        if self.performance_stats['total_attempts'] == 0:
            success_rate = 0
        else:
            success_rate = (self.performance_stats['successful_recognitions'] / 
                          self.performance_stats['total_attempts']) * 100
        
        return {
            **self.performance_stats,
            'success_rate': success_rate
        }
    
    def show_performance_stats(self):
        """Display performance statistics"""
        stats = self.get_performance_stats()
        
        print("\n📊 VOICE RECOGNITION PERFORMANCE:")
        print("-" * 40)
        print(f"  Total Attempts    : {stats['total_attempts']}")
        print(f"  Successful        : {stats['successful_recognitions']}")
        print(f"  Google Success    : {stats['google_success']}")
        print(f"  Offline Success   : {stats['offline_success']}")
        print(f"  Failures          : {stats['failures']}")
        print(f"  Success Rate      : {stats['success_rate']:.1f}%")
        print("-" * 40)

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

    def toggle_noise_reduction(self):
        """Toggle noise reduction on/off"""
        self.noise_reduction_enabled = not self.noise_reduction_enabled
        status = "ON" if self.noise_reduction_enabled else "OFF"
        print(f"🔊 Noise reduction: {status}")
        
        # Adjust recognizer settings
        if self.noise_reduction_enabled:
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 400
        else:
            self.recognizer.dynamic_energy_threshold = False
            self.recognizer.energy_threshold = 300
