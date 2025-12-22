print("=" * 70)
print("SMART VOICE CONTROL FOR POWERPOINT")
print("=" * 70)
print()
print("FITUR UTAMA:")
print("- Voice recognition dengan Google Speech API")
print("- Smart keyword detection dengan confidence score")
print("- Fuzzy Matching (Levenshtein Distance) untuk toleransi 80%+")
print("- Phonetic Algorithms (Soundex/Metaphone) untuk kesalahan pengucapan")
print("- Daftar Sinonim & Variasi untuk mendukung aksen berbeda")
print("- Voice-only mode untuk kontrol yang sederhana")
print("- Real-time feedback dan statistik")
print("- PowerPoint control yang smooth")
print()
print("KONTROL MODE:")
print("  Voice Mode    : Bicara perintah secara langsung")
print("  Help          : Katakan 'help' untuk bantuan")
print("  Exit          : Katakan 'stop' untuk keluar")
print()
print("=" * 70)

import time
import sys

from voice_detector import SmartVoiceDetector
from hybrid_voice_recognizer import HybridVoiceRecognizer
from powerpoint_controller import PowerPointController
from accessibility_popup import AccessibilityPopup

# Default untuk keamanan jika file diimport sebagai modul
is_windows = False


def main():
    # Flush input buffer untuk mencegah key press tak sengaja (Windows saja)
    if is_windows:
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except Exception:
            pass

    # Inisialisasi komponen
    print("\n" + "[INIT] " + "=" * 50)
    print("INITIALIZING SYSTEM...")
    print("=" * 50)

    detector = SmartVoiceDetector()
    ppt = PowerPointController()
    
    # Hybrid voice recognition (Google + offline fallback)
    voice = HybridVoiceRecognizer()

    # Initialize accessibility popup system
    popup = AccessibilityPopup()
    popup.start()
    ppt.set_popup_system(popup)

    # Connect popup to voice recognizer for real-time captioning
    popup.voice_recognizer = voice

    # List devices
    voice.list_audio_devices()

    # Coba deteksi device HP secara otomatis
    print("\n🎙️  MENCOBA MENDETEKSI MIKROFON HP...")
    detected_hp_device = None
    try:
        import pyaudio
        audio = pyaudio.PyAudio()
        for i in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:
                name = device_info.get('name', '').lower()
                # Cek untuk device HP yang aktif
                if ('oppo' in name or 'a53' in name or 'hands-free' in name or 'hf audio' in name) and device_info.get('maxInputChannels') > 0:
                    # Test apakah device bisa digunakan
                    try:
                        import speech_recognition as sr
                        test_mic = sr.Microphone(device_index=i)
                        with test_mic as source:
                            # Quick test - jika bisa buka source, device aktif
                            pass
                        detected_hp_device = i
                        print(f"✅ Terdeteksi device HP aktif: {i} - {device_info.get('name')}")
                        break
                    except:
                        print(f"⚠️  Device {i} terdeteksi tapi tidak aktif: {device_info.get('name')}")
                        continue
        audio.terminate()
    except Exception as e:
        print(f"⚠️  Gagal mendeteksi device HP: {e}")

    if detected_hp_device is not None:
        print(f"🎙️  Menggunakan device HP terdeteksi: {detected_hp_device}")
        voice.select_device(detected_hp_device)
    else:
        # Gunakan device 1 (Microphone Array Realtek) sebagai default
        print("\n🎙️  MENGGUNAKAN MICROPHONE ARRAY REALTEK (DEVICE 1) SEBAGAI DEFAULT")
        print("   Jika ingin mengganti, pilih 'y' di bawah ini")

        # Tanya apakah ingin ganti device
        try:
            change_device = input("Apakah Anda ingin mengubah sumber suara? (y/n): ").strip().lower()
            if change_device == 'y' or change_device == 'yes':
                print("\n🎙️  PILIH DEVICE AUDIO:")
                voice.list_audio_devices()
                device_choice = input("Masukkan nomor device (atau enter untuk default): ").strip()
                if device_choice.isdigit():
                    voice.select_device(int(device_choice))
                    print(f"✅ Device {device_choice} dipilih")
                else:
                    print("✅ Tetap menggunakan device 1 (Microphone Array Realtek)")
                    voice.select_device(1)
            else:
                print("✅ Menggunakan device 1 (Microphone Array Realtek)")
                voice.select_device(1)
        except Exception as e:
            print(f"⚠️  Error memilih device: {e}")
            print("✅ Menggunakan device 1 (Microphone Array Realtek)")
            voice.select_device(1)

    voice_success = voice.initialize()

    if not voice_success:
        print("\n[ERROR] Voice recognition gagal diinisialisasi!")
        print("Program tidak dapat berjalan tanpa voice mode.")
        input("\nTekan Enter untuk keluar...")
        return

    # Test microphone functionality (optional - will continue even if failed)
    print("\n🎙️  TESTING MICROPHONE...")
    test_result = voice.test_microphone(duration=2)  # Short test
    if not test_result:
        print("⚠️  MICROPHONE TEST GAGAL - TETAPI AKAN MELANJUTKAN...")
        print("💡 TIPS UNTUK LEBIH BAIK:")
        print("   • Bicara lebih keras dan jelas")
        print("   • Dekatkan mulut ke microphone")
        print("   • Pastikan lingkungan tenang")
        print("   • Jika masih bermasalah, periksa Settings > Sound")
        print()
        print("🔄 MELANJUTKAN KE MODE LISTENING...")
        import time
        time.sleep(2)  # Brief pause
    else:
        print("✅ Microphone test berhasil!")

    detector.show_help()

    print("\n" + "[READY] " + "=" * 50)
    print("SISTEM SIAP!")
    print("=" * 50)
    print("Mode: VOICE ONLY")
    print("Katakan 'help' untuk bantuan, 'stop' untuk keluar")
    print("\nINFO: BUKA POWERPOINT DAN TEKAN F5 UNTUK SLIDESHOW")
    print("INFO: KEMBALI KE WINDOW INI UNTUK KONTROL")
    print("=" * 50 + "\n")

    running = True

    try:
        while running:
            print("\n" + "-" * 60)
            print("BICARALAH SEKARANG...")
            print("-" * 60)

            # Listen for voice
            text = voice.listen()

            if text is None:
                # Tidak ada suara: lanjut listening
                print("    ... kembali ke listening ...")
                continue

            # Process command
            result = detector.detect(text)

            if result and result.get("command") != "unknown":
                feedback = ppt.execute_command(result)
                print(f"\n    {feedback}")

                if "score" in result:
                    print(f"    Skor: {result['score']}/{result.get('max_score', 10)}")

                cmd = result.get("command")
                if cmd == "stop":
                    print("\n" + "[STOP] " + "=" * 50)
                    print("PROGRAM DIHENTIKAN")
                    print("=" * 50)
                    running = False
                    break
                elif cmd == "help":
                    detector.show_help()
                elif cmd == "test":
                    print("\n" + "[TEST] " + "=" * 50)
                    print("TESTING MICROPHONE...")
                    print("=" * 50)
                    voice.test_microphone(duration=3)
                elif cmd == "noise":
                    voice.toggle_noise_reduction()

            else:
                score_val = result.get("score", 0) if result else 0
                feedback = ppt.execute_command({"command": "unknown", "score": score_val})
                print(f"\n    {feedback}")

                if result and "reason" in result:
                    print(f"    Alasan: {result['reason']}")

                print("    Tip: Katakan 'help' untuk bantuan")

            # Small delay
            time.sleep(0.3)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] PROGRAM DIHENTIKAN OLEH USER (Ctrl+C)")

    finally:
        # Final statistics
        print("\n" + "=" * 70)
        print("FINAL REPORT")
        print("=" * 70)
        ppt.show_statistics()

        # Speech history
        try:
            voice.show_history()
            voice.save_history()
        except AttributeError:
            print("History tidak tersedia.")

        # Stop popup system
        try:
            popup.stop()
        except:
            pass

        print("\n" + "[BYE] " + "=" * 50)
        print("TERIMA KASIH TELAH MENGGUNAKAN SMART VOICE CONTROL")
        print("=" * 50)

        input("\nTekan Enter untuk keluar...")


# ============================================
# RUN PROGRAM
# ============================================
if __name__ == "__main__":
    # Check requirements
    try:
        import pyautogui
    except ImportError:
        print("[ERROR] PyAutoGUI belum terinstall!")
        print("   Install dengan: pip install pyautogui")
        input("\nTekan Enter untuk keluar...")
        sys.exit(1)

    try:
        import speech_recognition as sr
    except ImportError:
        print("[WARN] SpeechRecognition belum terinstall")
        print("   Voice mode tidak akan tersedia")
        print("   Install dengan: pip install SpeechRecognition")
        sr = None
        time.sleep(2)

    # Check for Windows (msvcrt) or provide fallback
    try:
        import msvcrt  # noqa: F401
        is_windows = True
    except ImportError:
        print("[WARN] msvcrt tidak tersedia (bukan Windows?)")
        print("   Mode switch dengan tombol mungkin tidak bekerja")
        print("   Menggunakan input standar sebagai fallback")
        is_windows = False
        time.sleep(2)

    # Run main program
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Error fatal: {e}")
        print("Program dihentikan karena error.")
        input("\nTekan Enter untuk keluar...")
