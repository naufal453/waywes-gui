import gi
import subprocess
import time
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

class WaydroidGUI(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Waydroid in Weston")
        self.set_default_size(400, 400)

        # Fix transparency issue
        self.set_background_color()

        # Box to hold widgets
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(vbox)

        # Title label
        self.title_label = Gtk.Label(label="Waydroid in Weston GUI by Naufal453")
        vbox.append(self.title_label)

        # Main menu options
        self.main_menu = Gtk.ListBox()
        vbox.append(self.main_menu)

        # List of options
        options = [
            "1920x1080 Fullscreen", "1366x768 Fullscreen", "1920x1024 Windowed E2E", "1366x720 Windowed E2E",
            "1600x900 FHD Tablet Mode", "1024x600 HD Tablet Mode", "480x960 FHD Portrait Mode", "360x660 HD Portrait Mode", 
             "Exit"
        ]

        for option in options:
            button = Gtk.Button(label=option)
            button.connect("clicked", self.on_option_selected, option)
            self.main_menu.append(button)

        # Start monitoring Weston process
        GLib.timeout_add(2000, self.monitor_weston_process)

    def set_background_color(self):
        """Fix transparency issue by applying a solid background."""
        provider = Gtk.CssProvider()
        provider.load_from_data(b"window { background-color: #242424; }")
        style_context = self.get_style_context()
        style_context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def monitor_weston_process(self):
        """Check if Weston is running and hide GUI when it starts."""
        weston_pid = self.get_weston_pid()
        
        if weston_pid:
            self.hide()  # Hide GUI when Weston is running
            GLib.timeout_add(1000, self.wait_for_weston_termination, weston_pid)  # Check if Weston stops
        else:
            self.show()  # Show GUI when Weston is not running
            self.stop_waydroid()  # Ensure Waydroid stops
        
        return True  # Keep checking

    def wait_for_weston_termination(self, weston_pid):
        """Wait for Weston to close, then stop Waydroid."""
        try:
            subprocess.run(f"kill -0 {weston_pid}", shell=True, check=True)
            return True  # Weston is still running, keep checking
        except subprocess.CalledProcessError:
            self.show()  # Show GUI
            self.stop_waydroid()  # Stop Waydroid
            return False  # Stop checking

    def get_weston_pid(self):
        """Get the process ID (PID) of Weston."""
        try:
            result = subprocess.run("pgrep weston", shell=True, capture_output=True, text=True)
            return int(result.stdout.strip()) if result.stdout else None
        except ValueError:
            return None

    def stop_waydroid(self):
        """Stop the Waydroid session when Weston closes."""
        print("Weston closed! Stopping Waydroid session...")
        subprocess.run("waydroid session stop", shell=True)

    def on_option_selected(self, widget, option):
        if option == "Exit":
            self.close()
        elif option == "Extras":
            self.show_submenu()
        else:
            self.run_command(option)

    def run_command(self, option):
        """Run Waydroid in Weston with selected resolution."""
        resolutions = {
            "1920x1080 Fullscreen": "1920 1080",
            "1366x768 Fullscreen": "1366 768",
            "1920x1024 Windowed E2E": "1920 1024",
            "1366x720 Windowed E2E": "1366 720",
            "1600x900 FHD Tablet Mode": "1600 900",
            "1024x600 HD Tablet Mode": "1024 600",
            "480x960 FHD Portrait Mode": "480 960",
            "360x660 HD Portrait Mode": "360 660"
        }

        if option in resolutions:
            resolution = resolutions[option]

            # RUN WESTON IN BACKGROUND (Avoid freezing)
            subprocess.Popen(
                f"waydroid session stop && weston --width {resolution.split()[0]} --height {resolution.split()[1]} "
                "--shell=kiosk-shell.so --socket=wayland-1 &>/dev/null &", shell=True
            )
            
            # Give Weston time to start
            time.sleep(5)

            # RUN WAYDROID IN BACKGROUND
            subprocess.Popen(
                "WAYLAND_DISPLAY=wayland-1 XDG_SESSION_TYPE=wayland waydroid show-full-ui &>/dev/null &",
                shell=True
            )

    def show_submenu(self):
        """Display extra options in a dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="Choose an extra option:\n1. Add Script to Path\n2. Remove Script from Path\n3. FAQ\n4. Main Menu"
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("OK clicked")
        dialog.destroy()


# Run the GTK4 application
class MyApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.WaydroidGUI")

    def do_activate(self):
        win = WaydroidGUI(self)
        win.present()


app = MyApp()
app.run()

