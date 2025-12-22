# ============================================
# KELAS VOICE DETECTOR (SMART DETECTION)
# ============================================
class SmartVoiceDetector:
    def __init__(self):
        # Import libraries for fuzzy matching and phonetic algorithms
        try:
            from fuzzywuzzy import fuzz
            import jellyfish
            self.fuzzy_available = True
        except ImportError:
            print("⚠️  Fuzzy matching libraries not available. Install with: pip install fuzzywuzzy jellyfish")
            self.fuzzy_available = False

        # Wake words (frasa lengkap) untuk mengurangi false positive
        self.wake_words = {
            "next": {
                "phrases": ["next slide", "slide next", "lanjut slide", "slide lanjut", "next life", "life next", "next time", "time next", "neck slide", "nasi liwet", "net slide", "next side"],
                "weight": 10,
                "description": "Slide maju"
            },
            "previous": {
                "phrases": ["back slide", "slide back", "mundur slide", "slide mundur", "previous slide", "slide previous", "prev slide", "slide prev", "dextile", "dext slide", "backslide", "slide back", "bag slide", "pack slide", "bak slide", "preview slide", "brevious slide", "privy slide", "previous side", "prevu slide", "back side", "black slide"],
                "weight": 10,
                "description": "Slide mundur"
            },
            "open_slideshow": {
                "phrases": ["open slide show", "slide show open", "start slide show", "slide show start", "mulai slide show", "slide show mulai", "buka slide show", "slide show buka", "f5", "mulai presentasi", "presentasi mulai", "buka presentasi", "presentasi buka", "start presentation", "presentation start", "open slide", "open side show", "open slideshows"],
                "weight": 15,  # Ditingkatkan untuk prioritas
                "description": "Buka slideshow (F5)"
            },
            "close_slideshow": {
                "phrases": ["close slide show", "slide show close", "quit slide show", "slide show quit", "keluar slide show", "slide show keluar", "tutup slide show", "slide show tutup", "stop slide show", "slide show stop", "akhiri presentasi", "presentasi akhiri", "tutup presentasi", "presentasi tutup", "end presentation", "presentation end", "exit slideshow", "slideshow exit", "close slide", "close side show", "close slideshows"],
                "weight": 15,  # Tetap tinggi untuk close
                "description": "Tutup slideshow (ESC)"
            },
            "help": {
                "phrases": ["help menu", "menu help", "bantuan menu", "menu bantuan", "helm menu", "hal menu", "helmmu", "menu bantu", "menu bantuanmu", "menu bantuin", "held menu", "hell menu", "help me menu"],
                "weight": 8,
                "description": "Tampilkan bantuan"
            },
            "stop": {
                "phrases": ["stop program", "program stop", "berhenti program", "program berhenti", "stop", "berhenti", "stok program", "setiap program", "top program", "stop programnya", "stop progran"],
                "weight": 15,  # Tinggi untuk stop
                "description": "Stop program"
            },
            "test": {
                "phrases": ["test mic", "mic test", "test microphone", "microphone test", "test audio", "audio test"],
                "weight": 8,
                "description": "Test microphone"
            },
            "noise": {
                "phrases": ["toggle noise", "noise toggle", "noise reduction", "reduction noise", "noise on", "noise off"],
                "weight": 8,
                "description": "Toggle noise reduction"
            },
            "popup_on": {
                "phrases": ["popup on", "show popup", "popup show", "enable popup", "popup enable", "turn on popup", "popup turn on"],
                "weight": 8,
                "description": "Tampilkan popup bantu"
            },
            "popup_off": {
                "phrases": ["popup off", "hide popup", "popup hide", "disable popup", "popup disable", "turn off popup", "popup turn off"],
                "weight": 8,
                "description": "Sembunyikan popup bantu"
            },
            "caption_on": {
                "phrases": ["caption on", "start caption", "caption start", "enable caption", "caption enable", "turn on caption", "caption turn on", "live caption on", "caption live on"],
                "weight": 8,
                "description": "Tampilkan teks caption dan mulai live captioning real-time"
            },
            "caption_off": {
                "phrases": ["caption off", "stop caption", "caption stop", "disable caption", "caption disable", "turn off caption", "caption turn off", "live caption off", "caption live off"],
                "weight": 12,
                "description": "Teks caption berhenti dan sembunyikan live captioning real-time"
            },
            "change_language": {
                "phrases": ["change language", "language change", "switch language", "language switch", "ganti bahasa", "bahasa ganti"],
                "weight": 7,
                "description": "Change caption language"
            },
            "show_analytics": {
                "phrases": ["show analytics", "analytics show", "display analytics", "analytics display", "session stats", "stats session"],
                "weight": 7,
                "description": "Show session analytics"
            }
        }
        self.last_execution_time = 0
        self.cooldown_seconds = 2  # Cooldown 2 detik setelah eksekusi
    
    def detect(self, text):
        """Deteksi wake word dengan toleransi lebih (kurangi strictness)"""
        import time
        
        # Check cooldown
        current_time = time.time()
        if current_time - self.last_execution_time < self.cooldown_seconds:
            print(f"    ⏳ Cooldown aktif, tunggu {self.cooldown_seconds - (current_time - self.last_execution_time):.1f} detik lagi")
            return None
        
        if not text or len(text.strip()) < 2:  # Lebih toleran, minimal 2 karakter
            return None
        
        text_lower = text.lower().strip()
        results = []
        
        print(f"    📝 Memproses: '{text_lower}'")
        
        for command, data in self.wake_words.items():
            for phrase in data["phrases"]:
                score = 0
                # Exact match frasa lengkap mendapat bonus tertinggi
                if phrase in text_lower:
                    score = data["weight"] + 10
                # Kata kunci spesifik untuk membedakan open/close
                elif command == "open_slideshow" and any(word in text_lower for word in ["open", "start", "mulai", "buka", "f5"]):
                    if "slide" in text_lower or "show" in text_lower:
                        score = data["weight"] + 3
                elif command == "close_slideshow" and any(word in text_lower for word in ["close", "quit", "keluar", "tutup", "stop", "exit", "end", "akhiri"]):
                    if "slide" in text_lower or "show" in text_lower:
                        score = data["weight"] + 3
                # Partial match kata dari frasa (kurangi untuk menghindari false positive)
                elif any(word in text_lower for word in phrase.split() if len(word) > 3):  # Kata > 3 huruf
                    score = data["weight"] - 5  # Lebih dikurangi untuk strictness
                
                # Fuzzy Matching (Levenshtein Distance)
                if self.fuzzy_available and score == 0:
                    try:
                        from fuzzywuzzy import fuzz
                        import jellyfish
                        
                        # Hitung similarity ratio
                        similarity = fuzz.ratio(text_lower, phrase)
                        if similarity >= 80:  # Threshold 80%
                            score = data["weight"] + (similarity / 10)  # Bonus berdasarkan similarity
                        
                        # Phonetic Matching (Soundex/Metaphone)
                        if score == 0:
                            text_soundex = jellyfish.soundex(text_lower)
                            phrase_soundex = jellyfish.soundex(phrase)
                            if text_soundex == phrase_soundex and len(text_soundex) > 2:
                                score = data["weight"] + 2  # Bonus untuk phonetic match
                            
                            # Metaphone juga
                            text_metaphone = jellyfish.metaphone(text_lower)
                            phrase_metaphone = jellyfish.metaphone(phrase)
                            if text_metaphone == phrase_metaphone and len(text_metaphone) > 2:
                                score = max(score, data["weight"] + 2)
                    except Exception as e:
                        print(f"    ⚠️  Error in fuzzy/phonetic matching: {e}")
                
                if score > 0:
                    results.append({
                        "command": command,
                        "phrase": phrase,
                        "score": score,
                        "max_score": data["weight"] + 10,
                        "description": data["description"]
                    })
        
        if not results:
            return None
        
        # Special handling for conflicting commands
        text_lower = text.lower()
        if "captioning" in text_lower or "caption" in text_lower:
            # Prioritize stop_captioning over stop when captioning is mentioned
            captioning_results = [r for r in results if r["command"] == "stop_captioning"]
            if captioning_results:
                # Boost stop_captioning score if captioning is in the text
                for result in captioning_results:
                    result["score"] += 5
        
        results.sort(key=lambda x: x["score"], reverse=True)
        best_match = results[0]
        
        # Threshold lebih rendah untuk toleransi (karena recognition sering gagal)
        if best_match["score"] >= 6:  # Lebih rendah untuk toleransi homophone
            self.last_execution_time = current_time
            return best_match
        else:
            return {"command": "unknown", "score": best_match["score"], 
                   "reason": f"Score {best_match['score']} < threshold 6"}
    
    def show_help(self):
        """Tampilkan bantuan wake words"""
        print("\n" + "🔊 " + "="*50)
        print("📋 DAFTAR WAKE WORDS (FRASE LENGKAP):")
        print("="*50)
        
        for cmd, data in self.wake_words.items():
            print(f"\n🎯 {data['description'].upper()}:")
            phrases = ", ".join(data['phrases'])
            print(f"   Frasa: {phrases}")
        
        print(f"\n⏳ Cooldown: {self.cooldown_seconds} detik setelah setiap eksekusi")
        print("\n💡 FITUR TOLERANSI:")
        print("   • Fuzzy Matching: Mendeteksi frasa mirip (80%+ similarity)")
        print("   • Phonetic Algorithms: Mendeteksi kata dengan bunyi serupa")
        print("   • Daftar Sinonim: Mendukung variasi pengucapan")
        print("   • Accessibility Popup: Popup bantu untuk audiens difabel")
        print("\n💡 Gunakan frasa lengkap untuk hasil terbaik")
        print("\n" + "🎮 " + "="*50)
        print("KONTROL PROGRAM:")
        print("  Voice Mode: Bicara langsung")
        print("  Help      : Katakan 'help menu' untuk bantuan ini")
        print("  Popup     : Katakan 'popup on'/'popup off' untuk popup accessibility")
        print("  Caption   : Katakan 'caption on'/'caption off' untuk live caption")
        print("  Language  : Katakan 'change language' untuk ganti bahasa")
        print("  Analytics : Katakan 'show analytics' untuk statistik")
        print("  Exit      : Katakan 'stop program' untuk keluar")
        print("  Ctrl+C    : Emergency stop")
        print("="*50 + "\n")