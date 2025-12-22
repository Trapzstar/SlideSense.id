import pyautogui
from datetime import datetime

# ============================================
# KELAS POWERPOINT CONTROLLER
# ============================================
class PowerPointController:
    def __init__(self):
        self.stats = {
            "next": 0, "previous": 0, "stop": 0, 
            "help": 0, "unknown": 0, "total": 0,
            "open_slideshow": 0, "close_slideshow": 0,
            "popup_on": 0, "popup_off": 0,
            "caption_on": 0, "caption_off": 0,
            "change_language": 0, "show_analytics": 0
        }
        self.start_time = datetime.now()
        self.current_slide = 1
        self.total_slides = 10  # Default, can be updated
        self.popup_system = None  # Will be set by main app
        
    def execute_command(self, command_data):
        """Execute PowerPoint command based on detection"""
        self.stats["total"] += 1
        command = command_data["command"]
        
        try:
            if command == "next":
                pyautogui.press('right')
                self.stats["next"] += 1
                return f"✅ SLIDE MAJU! (Total: {self.stats['next']})"
                
            elif command == "previous":
                pyautogui.press('left')
                self.stats["previous"] += 1
                return f"✅ SLIDE MUNDUR! (Total: {self.stats['previous']})"
                
            elif command == "stop":
                self.stats["stop"] += 1
                return "🛑 PERINTAH STOP DITERIMA"
                
            elif command == "help":
                self.stats["help"] += 1
                return "📋 MENAMPILKAN BANTUAN..."
                
            elif command == "open_slideshow":
                pyautogui.press('f5')
                self.stats["open_slideshow"] += 1
                return f"✅ BUKA SLIDESHOW! (F5) (Total: {self.stats['open_slideshow']})"
                
            elif command == "close_slideshow":
                pyautogui.press('esc')
                self.stats["close_slideshow"] += 1
                return f"✅ TUTUP SLIDESHOW! (ESC) (Total: {self.stats['close_slideshow']})"
                
            elif command == "slide_selanjutnya":
                pyautogui.press('right')
                self.stats["next"] += 1  # Reuse next counter
                return f"✅ SLIDE SELANJUTNYA! (Total: {self.stats['next']})"
                
            elif command == "slide_sebelumnya":
                pyautogui.press('left')
                self.stats["previous"] += 1  # Reuse previous counter
                self.current_slide = max(1, self.current_slide - 1)
                self._update_popup_slide_info()
                return f"✅ SLIDE SEBELUMNYA! (Total: {self.stats['previous']})"
                
            elif command == "mode_switch":
                self.stats["mode_switches"] += 1
                return "🔄 BERALIH MODE..."
                
            elif command == "popup_on":
                if self.popup_system:
                    content = {
                        'title': '🎯 Accessibility Guide',
                        'text': 'Popup accessibility aktif\nGunakan voice commands untuk kontrol',
                        'progress': f'Slide {self.current_slide}/{self.total_slides}'
                    }
                    self.popup_system.show_popup(content)
                    self.stats["popup_on"] += 1
                    return "🎯 POPUP ACCESSIBILITY DITAMPILKAN!"
                else:
                    return "⚠️ POPUP SYSTEM TIDAK TERSEDIA"
                    
            elif command == "popup_off":
                if self.popup_system:
                    self.popup_system.hide_popup()
                    self.stats["popup_off"] += 1
                    return "🎯 POPUP ACCESSIBILITY DISEMBUNYIKAN!"
                else:
                    return "⚠️ POPUP SYSTEM TIDAK TERSEDIA"
                    
            elif command == "caption_on":
                if self.popup_system and hasattr(self.popup_system, 'start_real_time_captioning'):
                    voice_recognizer = getattr(self.popup_system, 'voice_recognizer', None)
                    if voice_recognizer:
                        self.popup_system.start_real_time_captioning(voice_recognizer)
                        self.stats["caption_on"] += 1
                        return "🎤 CAPTIONING DIMULAI - TEKS CAPTION DITAMPILKAN!"
                    else:
                        return "⚠️ VOICE RECOGNIZER TIDAK TERSEDIA"
                else:
                    return "⚠️ CAPTIONING SYSTEM TIDAK TERSEDIA"
                    
            elif command == "caption_off":
                if self.popup_system and hasattr(self.popup_system, 'stop_real_time_captioning'):
                    self.popup_system.stop_real_time_captioning()
                    self.stats["caption_off"] += 1
                    return "🎤 CAPTIONING DIHENTIKAN - TEKS CAPTION DISEMBUNYIKAN!"
                else:
                    return "⚠️ CAPTIONING SYSTEM TIDAK TERSEDIA"
                    
            elif command == "change_language":
                if self.popup_system and hasattr(self.popup_system, 'set_caption_language'):
                    # Cycle through available languages
                    languages = list(self.popup_system.get_available_languages().keys())
                    current_idx = languages.index(self.popup_system.current_language)
                    next_lang = languages[(current_idx + 1) % len(languages)]
                    self.popup_system.set_caption_language(next_lang)
                    self.stats["change_language"] += 1
                    return f"🌐 BAHASA DIGANTI KE: {self.popup_system.get_available_languages()[next_lang]}"
                else:
                    return "⚠️ MULTI-LANGUAGE SYSTEM TIDAK TERSEDIA"
                    
            elif command == "show_analytics":
                if self.popup_system and hasattr(self.popup_system, 'show_analytics_popup'):
                    self.popup_system.show_analytics_popup()
                    self.stats["show_analytics"] += 1
                    return "📊 ANALYTICS DITAMPILKAN!"
                else:
                    return "⚠️ ANALYTICS SYSTEM TIDAK TERSEDIA"
                
            elif command == "unknown":
                self.stats["unknown"] += 1
                return "⚠️  PERINTAH TIDAK DIKENALI"
                
            return "⚠️  PERINTAH TIDAK DIKENALI"
        except Exception as e:
            return f"❌ Error eksekusi: {str(e)[:50]}..."
    
    def set_popup_system(self, popup_system):
        """Set the accessibility popup system"""
        self.popup_system = popup_system
        
    def set_slide_count(self, total_slides: int):
        """Set total number of slides"""
        self.total_slides = total_slides
        
    def _update_popup_slide_info(self):
        """Update popup with current slide information"""
        if self.popup_system:
            self.popup_system.show_slide_info(
                self.current_slide, 
                self.total_slides,
                f"Slide {self.current_slide}"
            )
    
    def show_statistics(self):
        """Show statistics"""
        duration = datetime.now() - self.start_time
        minutes = duration.total_seconds() / 60
        
        print("\n" + "📊 " + "="*60)
        print("STATISTIK SESSION:")
        print("="*60)
        print(f"   Durasi          : {minutes:.1f} menit")
        print(f"   Total perintah  : {self.stats['total']}")
        print(f"   - Slide maju    : {self.stats['next']}")  
        print(f"   - Slide mundur  : {self.stats['previous']}")
        print(f"   - Buka slideshow: {self.stats['open_slideshow']}")
        print(f"   - Tutup slideshow: {self.stats['close_slideshow']}")
        print(f"   - Stop          : {self.stats['stop']}")
        print(f"   - Bantuan       : {self.stats['help']}")  
        print(f"   - Popup On      : {self.stats['popup_on']}")
        print(f"   - Popup Off     : {self.stats['popup_off']}")
        print(f"   - Caption On    : {self.stats['caption_on']}")
        print(f"   - Caption Off   : {self.stats['caption_off']}")
        print(f"   - Language Change: {self.stats['change_language']}")
        print(f"   - Show Analytics : {self.stats['show_analytics']}")
        print(f"   - Tidak dikenali: {self.stats['unknown']}")
        
        if self.stats['total'] > 0:
            success_rate = ((self.stats['next'] + self.stats['previous'] + self.stats['open_slideshow'] + self.stats['close_slideshow'] + self.stats['help']) / 
                          self.stats['total']) * 100
            print(f"   Success rate    : {success_rate:.1f}%")
        print("="*60)