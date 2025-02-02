import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class WaydroidGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="Waydroid in Weston")

        self.set_size_request(400, 400)
        self.set_border_width(10)

        # Box to hold widgets
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Title label
        self.title_label = Gtk.Label(label="This is a basic script to run Waydroid in Weston with different modes by K S Maan")
        vbox.pack_start(self.title_label, False, False, 0)

        # Main menu options
        self.main_menu = Gtk.ListBox()
        vbox.pack_start(self.main_menu, True, True, 0)

        # List of options
        options = [
            "1920x1080 Fullscreen", "1366x768 Fullscreen", "1920x1024 Windowed E2E", "1366x720 Windowed E2E",
            "1600x900 FHD Tablet Mode", "1024x600 HD Tablet Mode", "480x960 FHD Portrait Mode", "360x660 HD Portrait Mode", 
            "Extras", "Exit"
        ]

        for option in options:
            button = Gtk.Button(label=option)
            button.connect("clicked", self.on_option_selected, option)
            self.main_menu.add(button)

        self.main_menu.show_all()

        # Connect the window close event to stop Waydroid session
        self.connect("delete-event", self.on_delete_event)

    def on_delete_event(self, widget, event):
        # Stop the Waydroid session when the window is closed
        subprocess.run("waydroid session stop", shell=True)
        Gtk.main_quit()
        return False  # Allow the window to close

    def on_option_selected(self, widget, option):
        if option == "Exit":
            Gtk.main_quit()
        elif option == "Extras":
            self.show_submenu()
        else:
            self.run_command(option)

    def run_command(self, option):
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
            subprocess.run(f"waydroid session stop && weston --width {resolution.split()[0]} --height {resolution.split()[1]} --shell=kiosk-shell.so --socket=wayland-1 &>/dev/null & sleep 5 && WAYLAND_DISPLAY=wayland-1 XDG_SESSION_TYPE=wayland waydroid show-full-ui", shell=True)

    def show_submenu(self):
        dialog = Gtk.Dialog("Extras", self, 0, ("Cancel", Gtk.ResponseType.CANCEL, "Ok", Gtk.ResponseType.OK))
        box = dialog.get_content_area()
        label = Gtk.Label(label="Choose an extra option:\n1. Add Script to Path\n2. Remove Script from Path\n3. FAQ\n4. Main Menu")
        box.add(label)
        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("OK clicked")
        dialog.destroy()


# Run the GTK application
win = WaydroidGUI()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

