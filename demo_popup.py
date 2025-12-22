# ============================================
# DEMO ACCESSIBILITY POPUP
# ============================================
import time
import threading
from accessibility_popup import AccessibilityPopup

def demo_popup():
    """Demonstrate accessibility popup features"""

    # Create popup instance
    popup = AccessibilityPopup()

    # Update settings for demo
    popup.update_settings({
        'position': 'bottom-right',
        'size': (350, 180),
        'transparency': 0.9,
        'font_size': 16,
        'theme': 'dark'
    })

    # Start popup system
    popup.start()

    print("🎯 Accessibility Popup Demo")
    print("Popup akan muncul di kanan bawah layar")
    print("Tekan Ctrl+C untuk berhenti demo")
    print()

    try:
        # Demo sequence
        time.sleep(2)

        # 1. Show presentation start
        print("1. Menampilkan start presentasi...")
        popup.show_navigation_hint('start')
        time.sleep(3)

        # 2. Show slide information
        print("2. Menampilkan info slide...")
        popup.show_slide_info(1, 10, "Pendahuluan")
        time.sleep(3)

        # 3. Show navigation
        print("3. Menampilkan navigasi next...")
        popup.show_navigation_hint('next')
        time.sleep(2)

        # 4. Show next slide
        print("4. Menampilkan slide berikutnya...")
        popup.show_slide_info(2, 10, "Isi Utama")
        time.sleep(3)

        # 5. Show caption
        print("5. Menampilkan caption...")
        popup.show_caption("Ini adalah contoh teks caption untuk audiens difabel")
        time.sleep(4)

        # 6. Show timer
        print("6. Menampilkan timer...")
        popup.show_timer("00:05:30", "00:24:30")
        time.sleep(3)

        # 7. Toggle visibility
        print("7. Toggle popup visibility...")
        popup.toggle_popup()
        time.sleep(2)
        popup.toggle_popup()
        time.sleep(2)

        print("✅ Demo selesai!")

    except KeyboardInterrupt:
        print("\n⏹️  Demo dihentikan oleh user")

    finally:
        # Cleanup
        popup.stop()
        print("🧹 Cleanup selesai")

if __name__ == "__main__":
    demo_popup()