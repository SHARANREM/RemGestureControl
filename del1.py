import time
import win32gui
import win32process
import psutil


class AppDetector:
    BROWSERS = ["chrome.exe", "brave.exe", "msedge.exe", "firefox.exe"]

    def get_active_app_name(self):
        """
        Returns context-aware app name.
        Example:
            chrome.exe:youtube
            brave.exe:figma
            explorer.exe
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return "unknown"

            # Get process
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            exe_name = process.name().lower()

            # Get window title
            window_title = win32gui.GetWindowText(hwnd)

            # If browser, extract site name
            if exe_name in self.BROWSERS and window_title:
                site_name = self.extract_site_name(window_title)
                if site_name:
                    return f"{exe_name}:{site_name}"

            return exe_name

        except Exception as e:
            print(f"Error detecting active app: {e}")
            return "unknown"

    def extract_site_name(self, title):
        """
        Extract site name from browser window title.
        Example titles:
            "YouTube - Google Chrome"
            "Figma – Brave"
        """
        # Remove browser suffix
        separators = [" - ", " – ", "|"]

        for sep in separators:
            if sep in title:
                site = title.split(sep)[0]
                return site.strip().lower()

        return title.strip().lower()


def monitor_active_app(check_interval=1):
    detector = AppDetector()
    last_app = None

    print("Monitoring active application... Press Ctrl+C to stop.\n")

    try:
        while True:
            current_app = detector.get_active_app_name()

            if current_app != last_app:
                print(f"Active App: {current_app}")
                last_app = current_app

            time.sleep(check_interval)

    except KeyboardInterrupt:
        print("\nStopped monitoring.")


if __name__ == "__main__":
    monitor_active_app()