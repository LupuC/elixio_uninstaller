import tkinter as tk
from tkinter import ttk, messagebox  # Importing necessary tkinter modules
import winreg  # Module for accessing Windows Registry
from datetime import datetime  # For date and time operations
import threading  # For threading support
import customtkinter  # Custom module for tkinter widgets and appearance
import subprocess  # For executing subprocesses
import requests

#release update

app_version = "1.0"
def check_for_updates():
    repo_owner = 'LupuC'
    repo_name = 'elixio_uninstaller'
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            release_info = response.json()
            latest_version = release_info['tag_name']  # Assuming tags are used for releases
            current_version = app_version  # Replace with your actual version retrieval method

            if latest_version != current_version:
                messagebox.showinfo("Update Available", f"A new version ({latest_version}) is available!")
            else:
                messagebox.showinfo("No Updates", "You are using the latest version.")

        else:
            messagebox.showerror("Error", f"Failed to check for updates: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check for updates: {e}")



# Function to fetch installed applications from Windows Registry
def get_installed_apps():
    installed_apps = []
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for reg_path in reg_paths:
        try:
            # Connect to the Windows Registry
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            reg_key = winreg.OpenKey(reg, reg_path)

            # Iterate through each subkey in the registry path
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    app_key_name = winreg.EnumKey(reg_key, i)  # Get the name of the subkey
                    app_key = winreg.OpenKey(reg_key, app_key_name)  # Open the subkey

                    # Fetch application information from the subkey
                    app_name = None
                    app_size_bytes = None
                    app_install_date_str = None

                    try:
                        app_name = winreg.QueryValueEx(app_key, "DisplayName")[0]  # Get display name
                    except FileNotFoundError:
                        pass

                    try:
                        app_size_bytes = winreg.QueryValueEx(app_key, "EstimatedSize")[0]  # Get size
                    except FileNotFoundError:
                        pass

                    try:
                        app_install_date_str = winreg.QueryValueEx(app_key, "InstallDate")[0]  # Get install date
                    except FileNotFoundError:
                        pass

                    # Convert size to readable format
                    app_size = convert_size(app_size_bytes) if app_size_bytes else "Unknown"
                    # Format install date
                    app_install_date = format_install_date(app_install_date_str) if app_install_date_str else "Unknown"

                    # Add application to list if it's not already present
                    if app_name and not any(app["name"] == app_name for app in installed_apps):
                        installed_apps.append({
                            "name": app_name,
                            "size": app_size,
                            "size_bytes": app_size_bytes if app_size_bytes else 0,
                            "installed_on": app_install_date
                        })

                    winreg.CloseKey(app_key)  # Close the subkey
                except Exception as e:
                    print(f"Error fetching application information: {e}")

            winreg.CloseKey(reg_key)  # Close the registry key
        except FileNotFoundError:
            continue

    return installed_apps

# Function to convert size from bytes to readable format
def convert_size(size_kb):
    size_bytes = size_kb * 1024
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"

# Function to format installation date
def format_install_date(install_date_str):
    try:
        install_date = datetime.strptime(install_date_str, '%Y%m%d')
        return install_date.strftime('%Y-%m-%d')
    except ValueError as e:
        print(f"Error formatting install date: {e}")
        return "Unknown"

# Function to populate the Treeview with installed applications
def populate_treeview():
    global installed_apps
    installed_apps = get_installed_apps()

    # Insert each application into the Treeview
    for app in installed_apps:
        treeview.insert("", "end", values=(app["name"], app["size"], app["installed_on"]))

    # Adjust column widths based on content
    max_size_width = max([len(app["size"]) for app in installed_apps])
    treeview.column("Size", width=max_size_width * 10)

    max_install_width = max([len(app["installed_on"]) for app in installed_apps])
    treeview.column("Installed On", width=max_install_width * 10)

    # Update the loaded information label with total count and size
    update_loaded_info()
    loading_indicator.stop()

# Function to fetch uninstall command for a given application
def get_uninstall_command(app_name):
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for reg_path in reg_paths:
        try:
            reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            reg_key = winreg.OpenKey(reg, reg_path)

            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    app_key_name = winreg.EnumKey(reg_key, i)
                    app_key = winreg.OpenKey(reg_key, app_key_name)

                    try:
                        display_name = winreg.QueryValueEx(app_key, "DisplayName")[0]
                        if display_name == app_name:
                            uninstall_string = winreg.QueryValueEx(app_key, "UninstallString")[0]
                            return uninstall_string
                    except FileNotFoundError:
                        pass

                    winreg.CloseKey(app_key)
                except Exception as e:
                    print(f"Error fetching uninstall command: {e}")

            winreg.CloseKey(reg_key)
        except FileNotFoundError:
            continue

    return None

# Function to sort applications by name
def sort_by_name():
    treeview.delete(*treeview.get_children())
    for app in sorted(installed_apps, key=lambda x: x["name"].lower()):
        treeview.insert("", "end", values=(app["name"], app["size"], app["installed_on"]))

# Function to sort applications by size
def sort_by_size():
    treeview.delete(*treeview.get_children())
    for app in sorted(installed_apps, key=lambda x: x["size_bytes"]):
        treeview.insert("", "end", values=(app["name"], app["size"], app["installed_on"]))

# Function to sort applications by installation date
def sort_by_date():
    treeview.delete(*treeview.get_children())
    for app in sorted(installed_apps, key=lambda x: x["installed_on"]):
        treeview.insert("", "end", values=(app["name"], app["size"], app["installed_on"]))

# Function to handle right-click context menu on Treeview
def on_right_click(event):
    item = treeview.identify_row(event.y)
    if item:
        treeview.selection_set(item)
        context_menu.post(event.x_root, event.y_root)

# Function to update loaded information label with current count and size
def update_loaded_info():
    loaded_apps_count = len(installed_apps)
    total_size_gb = sum([app["size_bytes"] / (1024 * 1024 * 1024) for app in installed_apps])
    loaded_info_label.configure(text=f"Loaded {loaded_apps_count} programs, total {total_size_gb:.2f} GB")

# Class for custom loading indicator
class LoadingIndicator(customtkinter.CTkLabel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.characters = ['|', '/', '-', '\\']
        self.index = 0
        self.animate = False

    def start(self):
        self.animate = True
        self._animate()

    def stop(self):
        self.animate = False
        self.configure(text="")

    def _animate(self):
        if self.animate:
            self.configure(text=self.characters[self.index])
            self.index = (self.index + 1) % len(self.characters)
            self.after(100, self._animate)




# Main function to initialize the application
def main():
    global root, frame, treeview, vsb, loaded_info_label, loading_indicator, loaded_info_label2, context_menu, installed_apps

    # Create main tkinter window
    root = customtkinter.CTk()
    root.title("Elixio Uninstaller")
    root.geometry("500x700")

    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")

    # Create main frame for widgets
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)

    # Create Treeview widget to display installed apps
    treeview = ttk.Treeview(frame, columns=("Name", "Size", "Installed On"), show="headings")
    treeview.heading("Name", text="Name", command=sort_by_name)
    treeview.heading("Size", text="Size", command=sort_by_size)
    treeview.heading("Installed On", text="Installed On", command=sort_by_date)

    # Create vertical scrollbar for Treeview
    vsb = customtkinter.CTkScrollbar(frame, command=treeview.yview)
    treeview.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")

    treeview.pack(fill=tk.BOTH, expand=True)

    # Create label to display loading information
    loaded_info_label = customtkinter.CTkLabel(root, text="Loading apps...")
    loaded_info_label.pack(side=tk.LEFT, padx=10, pady=5)

    # Create custom loading indicator
    loading_indicator = LoadingIndicator(root)
    loading_indicator.pack(side=tk.LEFT, padx=10, pady=5)

    # Create label to display version information
    loaded_info_label2 = customtkinter.CTkLabel(root, text=app_version)
    loaded_info_label2.pack(side=tk.RIGHT, padx=10, pady=5)

    # Create right-click context menu for Treeview
    context_menu = tk.Menu(root, tearoff=False)
    context_menu.add_command(label="Uninstall", command=uninstall_selected)
    treeview.bind("<Button-3>", on_right_click)

    check_for_updates()

    # Fetch and display installed applications
    fetch_data()

    # Start the tkinter main loop
    root.mainloop()

# Function to fetch data and populate the Treeview in a separate thread
def fetch_data():
    loading_indicator.start()
    thread = threading.Thread(target=populate_treeview)
    thread.start()

# Function to handle application uninstallation
def uninstall_selected(event=None):
    selected_item = treeview.selection()
    if selected_item:
        item = treeview.item(selected_item, "values")
        app_name = item[0]

        uninstall_cmd = get_uninstall_command(app_name)

        if uninstall_cmd:
            try:
                threading.Thread(target=lambda: subprocess.run(uninstall_cmd, shell=True)).start()
                # Remove uninstalled app from Treeview and installed_apps list
                for app in installed_apps:
                    if app["name"] == app_name:
                        installed_apps.remove(app)
                        break
                update_loaded_info()  # Update loaded information label
                treeview.delete(selected_item)  # Remove from Treeview
            except Exception as e:
                messagebox.showerror("Error", f"Failed to uninstall {app_name}: {e}")
        else:
            messagebox.showerror("Error", f"Uninstall command for {app_name} not found.")

# Start the main function if this script is executed directly
if __name__ == "__main__":
    main()