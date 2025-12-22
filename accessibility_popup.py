# ============================================
# ACCESSIBILITY POPUP OVERLAY
# ============================================
import tkinter as tk
import customtkinter as ctk
import threading
import time
from typing import Optional, Tuple, Dict, Any
import pyautogui
import win32gui
import win32con
import win32api
from datetime import datetime, timedelta
import json
import os

class AccessibilityPopup:
    """
    Popup overlay untuk membantu audiens difabel dalam presentasi fullscreen
    Enhanced with real-time captioning, multi-language support, and analytics
    """

    def __init__(self):
        self.window: Optional[ctk.CTk] = None
        self.is_visible = False
        self.current_content: Dict[str, Any] = {}
        self.thread: Optional[threading.Thread] = None
        self.running = False

        # Real-time captioning
        self.caption_thread: Optional[threading.Thread] = None
        self.caption_running = False
        self.last_caption_time = time.time()
        self.caption_buffer = []
        self.caption_language = "id"  # Default Indonesian

        # Multi-language support
        self.available_languages = {
            "id": "Bahasa Indonesia",
            "en": "English",
            "es": "Español",
            "fr": "Français",
            "de": "Deutsch",
            "ja": "日本語",
            "ko": "한국어",
            "zh": "中文"
        }
        self.current_language = "id"

        # Analytics
        self.analytics = {
            "start_time": datetime.now(),
            "popup_shown_count": 0,
            "caption_displayed_count": 0,
            "language_switches": 0,
            "total_caption_length": 0,
            "interaction_events": [],
            "performance_metrics": {
                "avg_popup_show_time": 0,
                "total_popup_duration": 0,
                "caption_update_frequency": 0
            }
        }
        self.analytics_file = "popup_analytics.json"

        # Default settings
        self.settings = {
            'position': 'bottom-right',  # top-left, top-right, bottom-left, bottom-right
            'size': (300, 150),
            'transparency': 0.85,
            'font_size': 14,
            'auto_hide': True,
            'hide_delay': 5,  # seconds
            'theme': 'dark'  # light, dark, system
        }

    def create_overlay_window(self):
        """Create the overlay window with proper settings"""
        if self.window:
            return

        # Create main window
        self.window = ctk.CTk()
        self.window.title("Accessibility Overlay")
        self.window.geometry(f"{self.settings['size'][0]}x{self.settings['size'][1]}")
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', self.settings['transparency'])
        self.window.overrideredirect(True)  # Remove window borders

        # Set theme
        ctk.set_appearance_mode(self.settings['theme'])

        # Create content frame
        self.content_frame = ctk.CTkFrame(self.window)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title label
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="🎯 Accessibility Guide",
            font=ctk.CTkFont(size=self.settings['font_size']+2, weight="bold")
        )
        self.title_label.pack(pady=(5, 10))

        # Content label
        self.content_label = ctk.CTkLabel(
            self.content_frame,
            text="Ready for presentation...",
            font=ctk.CTkFont(size=self.settings['font_size']),
            wraplength=self.settings['size'][0] - 20
        )
        self.content_label.pack(pady=(0, 10))

        # Progress indicator
        self.progress_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=ctk.CTkFont(size=self.settings['font_size']-2)
        )
        self.progress_label.pack(pady=(0, 5))

        # Position window
        self.update_position()

        # Make window click-through (optional)
        self.make_click_through()

    def make_click_through(self):
        """Make window click-through so it doesn't interfere with presentation"""
        try:
            hwnd = self.window.winfo_id()
            # WS_EX_TRANSPARENT makes window click-through
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                 win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TRANSPARENT)
        except:
            pass  # Fallback if pywin32 not available

    def update_position(self):
        """Update window position based on settings"""
        if not self.window:
            return

        screen_width, screen_height = pyautogui.size()
        win_width, win_height = self.settings['size']

        if self.settings['position'] == 'top-left':
            x, y = 20, 20
        elif self.settings['position'] == 'top-right':
            x, y = screen_width - win_width - 20, 20
        elif self.settings['position'] == 'bottom-left':
            x, y = 20, screen_height - win_height - 20
        elif self.settings['position'] == 'bottom-right':
            x, y = screen_width - win_width - 20, screen_height - win_height - 20
        else:
            x, y = screen_width - win_width - 20, screen_height - win_height - 20

        self.window.geometry(f"{win_width}x{win_height}+{x}+{y}")

    def show_popup(self, content: Dict[str, Any]):
        """Show popup with specific content"""
        self.current_content = content

        if not self.window:
            self.create_overlay_window()

        # Update content
        title = content.get('title', '🎯 Accessibility Guide')
        text = content.get('text', 'No content')
        progress = content.get('progress', '')

        self.title_label.configure(text=title)
        self.content_label.configure(text=text)
        self.progress_label.configure(text=progress)

        if not self.is_visible:
            self.window.deiconify()
            self.is_visible = True
            self.analytics["popup_shown_count"] += 1
            self.log_interaction("popup_shown", {"content_type": content.get('title', 'Unknown')})

        # Auto-hide if enabled
        if self.settings['auto_hide']:
            self.window.after(self.settings['hide_delay'] * 1000, self.hide_popup)

    def hide_popup(self):
        """Hide the popup"""
        if self.window and self.is_visible:
            self.window.withdraw()
            self.is_visible = False

    def toggle_popup(self):
        """Toggle popup visibility"""
        if self.is_visible:
            self.hide_popup()
        else:
            self.show_popup(self.current_content)

    def update_settings(self, new_settings: Dict[str, Any]):
        """Update popup settings"""
        self.settings.update(new_settings)

        if self.window:
            # Apply new settings
            self.window.attributes('-alpha', self.settings['transparency'])
            self.update_position()

            # Update fonts
            self.title_label.configure(font=ctk.CTkFont(size=self.settings['font_size']+2, weight="bold"))
            self.content_label.configure(font=ctk.CTkFont(size=self.settings['font_size']))
            self.progress_label.configure(font=ctk.CTkFont(size=self.settings['font_size']-2))

    def start(self):
        """Start the overlay system"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_overlay, daemon=True)
            self.thread.start()

    def stop(self):
        """Stop the overlay system"""
        self.running = False
        if self.window:
            self.window.quit()
            self.window.destroy()
            self.window = None

    def _run_overlay(self):
        """Main overlay loop"""
        while self.running:
            if self.window:
                try:
                    self.window.update_idletasks()
                    self.window.update()
                except:
                    break
            time.sleep(0.1)

    # Predefined content templates
    def show_slide_info(self, slide_number: int, total_slides: int, title: str = ""):
        """Show current slide information"""
        content = {
            'title': f'📊 Slide {slide_number}/{total_slides}',
            'text': f'{title}' if title else f'Slide {slide_number} of {total_slides}',
            'progress': f'Progress: {slide_number}/{total_slides}'
        }
        self.show_popup(content)

    def show_navigation_hint(self, direction: str):
        """Show navigation hint"""
        hints = {
            'next': {'title': '➡️ Next Slide', 'text': 'Moving to next slide...'},
            'previous': {'title': '⬅️ Previous Slide', 'text': 'Going back to previous slide...'},
            'start': {'title': '🎬 Presentation Start', 'text': 'Presentation has begun'},
            'end': {'title': '🏁 Presentation End', 'text': 'Presentation finished'}
        }

        content = hints.get(direction, {'title': '🎯 Navigation', 'text': direction})
        self.show_popup(content)

    def show_caption(self, text: str):
        """Show caption/subtitle"""
        content = {
            'title': '📝 Caption',
            'text': text,
            'progress': ''
        }
        self.show_popup(content)

    def show_timer(self, elapsed: str, remaining: str = ""):
        """Show presentation timer"""
        content = {
            'title': '⏱️ Timer',
            'text': f'Elapsed: {elapsed}',
            'progress': f'Remaining: {remaining}' if remaining else ''
        }
        self.show_popup(content)

    # ===== REAL-TIME CAPTIONING METHODS =====

    def start_real_time_captioning(self, voice_recognizer):
        """Start real-time captioning from voice input"""
        if self.caption_running:
            return

        self.caption_running = True
        self.caption_thread = threading.Thread(
            target=self._captioning_loop,
            args=(voice_recognizer,),
            daemon=True
        )
        self.caption_thread.start()
        print("🎤 Real-time captioning started")

    def stop_real_time_captioning(self):
        """Stop real-time captioning"""
        self.caption_running = False
        if self.caption_thread:
            self.caption_thread.join(timeout=1.0)
        print("🎤 Real-time captioning stopped")

    def _captioning_loop(self, voice_recognizer):
        """Main captioning loop"""
        while self.caption_running:
            try:
                # Listen for short audio segments
                text = voice_recognizer.listen(timeout=2, phrase_limit=3)

                if text and len(text.strip()) > 0:
                    # Translate if needed
                    translated_text = self._translate_text(text, self.current_language)

                    # Add to buffer
                    self.caption_buffer.append({
                        'original': text,
                        'translated': translated_text,
                        'timestamp': datetime.now(),
                        'language': self.current_language
                    })

                    # Keep only last 3 captions
                    if len(self.caption_buffer) > 3:
                        self.caption_buffer.pop(0)

                    # Update popup with latest caption
                    self._update_caption_display()

                    # Update analytics
                    self.analytics["caption_displayed_count"] += 1
                    self.analytics["total_caption_length"] += len(text)

                    self.last_caption_time = time.time()

            except Exception as e:
                print(f"Captioning error: {e}")
                time.sleep(0.5)

            time.sleep(0.1)

    def _translate_text(self, text: str, target_lang: str) -> str:
        """Translate text to target language (simplified version)"""
        if target_lang == "id":
            return text  # Already in Indonesian

        try:
            # Simple translation mapping (in production, use Google Translate API)
            translations = {
                "next slide": {
                    "en": "next slide",
                    "es": "siguiente diapositiva",
                    "fr": "diapositive suivante",
                    "de": "nächste Folie",
                    "ja": "次のスライド",
                    "ko": "다음 슬라이드",
                    "zh": "下一张幻灯片"
                },
                "previous slide": {
                    "en": "previous slide",
                    "es": "diapositiva anterior",
                    "fr": "diapositive précédente",
                    "de": "vorherige Folie",
                    "ja": "前のスライド",
                    "ko": "이전 슬라이드",
                    "zh": "上一张幻灯片"
                },
                "open slideshow": {
                    "en": "open slideshow",
                    "es": "abrir presentación",
                    "fr": "ouvrir présentation",
                    "de": "Präsentation öffnen",
                    "ja": "スライドショーを開く",
                    "ko": "슬라이드쇼 열기",
                    "zh": "打开幻灯片"
                },
                "close slideshow": {
                    "en": "close slideshow",
                    "es": "cerrar presentación",
                    "fr": "fermer présentation",
                    "de": "Präsentation schließen",
                    "ja": "スライドショーを閉じる",
                    "ko": "슬라이드쇼 닫기",
                    "zh": "关闭幻灯片"
                }
            }

            # Check if text matches known phrases
            for key, langs in translations.items():
                if key.lower() in text.lower():
                    return langs.get(target_lang, text)

            # For unknown text, return original with language indicator
            return f"[{self.available_languages.get(target_lang, target_lang)}] {text}"

        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def _update_caption_display(self):
        """Update popup with current caption buffer"""
        if not self.caption_buffer:
            return

        latest_caption = self.caption_buffer[-1]
        content = {
            'title': f'🎤 Live Caption ({self.available_languages[self.current_language]})',
            'text': latest_caption['translated'],
            'progress': f"Original: {latest_caption['original']}"
        }
        self.show_popup(content)

    # ===== MULTI-LANGUAGE SUPPORT METHODS =====

    def set_caption_language(self, language_code: str):
        """Set caption language"""
        if language_code in self.available_languages:
            old_lang = self.current_language
            self.current_language = language_code
            self.analytics["language_switches"] += 1

            print(f"🌐 Caption language changed: {self.available_languages[old_lang]} → {self.available_languages[language_code]}")

            # Update current caption if exists
            if self.caption_buffer:
                self._update_caption_display()
        else:
            print(f"❌ Unsupported language: {language_code}")

    def get_available_languages(self) -> Dict[str, str]:
        """Get list of available languages"""
        return self.available_languages.copy()

    # ===== ANALYTICS METHODS =====

    def log_interaction(self, event_type: str, details: Dict[str, Any] = None):
        """Log user interaction for analytics"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'details': details or {}
        }
        self.analytics['interaction_events'].append(event)

        # Keep only last 100 events
        if len(self.analytics['interaction_events']) > 100:
            self.analytics['interaction_events'].pop(0)

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        duration = datetime.now() - self.analytics['start_time']
        hours_active = duration.total_seconds() / 3600

        summary = {
            'session_duration_hours': round(hours_active, 2),
            'popup_shown_count': self.analytics['popup_shown_count'],
            'caption_displayed_count': self.analytics['caption_displayed_count'],
            'language_switches': self.analytics['language_switches'],
            'avg_captions_per_hour': round(self.analytics['caption_displayed_count'] / max(hours_active, 0.01), 2),
            'total_caption_characters': self.analytics['total_caption_length'],
            'current_language': self.available_languages.get(self.current_language, self.current_language),
            'performance_metrics': self.analytics['performance_metrics'].copy()
        }

        return summary

    def save_analytics(self):
        """Save analytics to file"""
        try:
            analytics_data = {
                'session_end': datetime.now().isoformat(),
                'summary': self.get_analytics_summary(),
                'full_data': self.analytics
            }

            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(analytics_data, f, indent=2, ensure_ascii=False)

            print(f"📊 Analytics saved to {self.analytics_file}")

        except Exception as e:
            print(f"❌ Failed to save analytics: {e}")

    def show_analytics_popup(self):
        """Show analytics in popup"""
        summary = self.get_analytics_summary()

        content = {
            'title': '📊 Session Analytics',
            'text': f"""Duration: {summary['session_duration_hours']}h
Popups: {summary['popup_shown_count']}
Captions: {summary['caption_displayed_count']}
Language: {summary['current_language']}
Avg Captions/Hour: {summary['avg_captions_per_hour']}""",
            'progress': f"Total Characters: {summary['total_caption_characters']}"
        }
        self.show_popup(content)