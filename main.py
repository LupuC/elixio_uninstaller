import tkinter as tk
from tkinter import ttk, messagebox
import winreg
from datetime import datetime
import threading
import customtkinter
import subprocess
import requests
import shutil
import json
import os
import sys


class ElixioUninstaller:
    def __init__(self):
        self.installed_apps = []
        self.config = self.load_config()
        self.sort_order = {"Name": True, "Size": True, "Installed On": True}
        self.init_ui()

    def load_config(self):
        try:
            with open('config.json') as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            messagebox.showerror("Error", "config.json not found. Please reinstall the application.")
            sys.exit(1)

    def init_ui(self):
        self.root = customtkinter.CTk()
        self.root.title(f"Elixio Uninstaller")
        self.root.geometry("600x800")

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        self.create_main_frame()
        self.create_search_bar()
        self.create_treeview()
        self.create_info_bar()
        self.create_context_menu()
        self.create_buttons()

        self.check_for_updates()
        self.fetch_data()

    def create_main_frame(self):
        self.main_frame = customtkinter.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def create_search_bar(self):
        search_frame = customtkinter.CTkFrame(self.main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        search_label = customtkinter.CTkLabel(search_frame, text="Search apps:")
        search_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_search)
        search_entry = customtkinter.CTkEntry(search_frame, textvariable=self.search_var,
                                              placeholder_text="Enter app name...")
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def create_treeview(self):
        columns = ("Name", "Size", "Installed On")
        self.treeview = ttk.Treeview(self.main_frame, columns=columns, show="headings", style="Custom.Treeview")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview", background="#2a2d2e", foreground="white", fieldbackground="#2a2d2e",
                        borderwidth=0)
        style.map('Custom.Treeview', background=[('selected', '#347083')])
        style.configure("Custom.Treeview.Heading", background="#347083", foreground="white", relief="flat")
        style.map("Custom.Treeview.Heading", background=[('active', '#2a2d2e')])

        for col in columns:
            self.treeview.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.treeview.column(col, width=100)

        self.scrollbar = customtkinter.CTkScrollbar(self.main_frame, command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.scrollbar.set)

        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.treeview.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<<TreeviewSelect>>", lambda event: self.root.focus_set())

    def create_info_bar(self):
        self.info_frame = customtkinter.CTkFrame(self.root)
        self.info_frame.pack(fill=tk.X, padx=20, pady=10)

        self.loaded_info_label = customtkinter.CTkLabel(self.info_frame, text="Loading apps...")
        self.loaded_info_label.pack(side=tk.LEFT)

        self.loading_indicator = LoadingIndicator(self.info_frame)
        self.loading_indicator.pack(side=tk.LEFT, padx=10)

        version_label = customtkinter.CTkLabel(self.info_frame, text=f"{self.config['version']}")
        version_label.pack(side=tk.RIGHT)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=False)
        self.context_menu.add_command(label="Uninstall", command=self.uninstall_selected)

    def create_buttons(self):
        button_frame = customtkinter.CTkFrame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)

        refresh_button = customtkinter.CTkButton(button_frame, text="Refresh", command=self.refresh_apps)
        refresh_button.pack(side=tk.LEFT)

        uninstall_button = customtkinter.CTkButton(button_frame, text="Uninstall Selected",
                                                   command=self.uninstall_selected)
        uninstall_button.pack(side=tk.LEFT, padx=5)

    def update_search(self, *args):
        search_term = self.search_var.get().lower()
        self.treeview.delete(*self.treeview.get_children())
        for app in self.installed_apps:
            if search_term in app["name"].lower():
                self.treeview.insert("", "end", values=(app["name"], app["size"], app["installed_on"]))

    def fetch_data(self):
        self.loading_indicator.start()
        threading.Thread(target=self.populate_treeview, daemon=True).start()

    def populate_treeview(self):
        self.installed_apps = self.get_installed_apps()
        self.root.after(0, self.update_treeview)

    def update_treeview(self):
        self.treeview.delete(*self.treeview.get_children())
        max_size_width = max(len(app["size"]) for app in self.installed_apps)
        max_date_width = max(len(app["installed_on"]) for app in self.installed_apps)

        self.treeview.column("Size", width=max_size_width * 10)
        self.treeview.column("Installed On", width=max_date_width * 10)

        # Calculate remaining width for the Name column
        total_width = self.main_frame.winfo_width()
        name_width = total_width - (max_size_width * 10) - (max_date_width * 10) - 20  # 20 for scrollbar
        self.treeview.column("Name", width=max(name_width, 200))  # Ensure minimum width of 200

        for app in self.installed_apps:
            self.treeview.insert("", "end", values=(app["name"], app["size"], app["installed_on"]))
        self.update_loaded_info()
        self.loading_indicator.stop()

    def get_installed_apps(self):
        apps = []
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for reg_root, reg_path in reg_paths:
            try:
                with winreg.OpenKey(reg_root, reg_path) as reg_key:
                    for i in range(winreg.QueryInfoKey(reg_key)[0]):
                        try:
                            app_key_name = winreg.EnumKey(reg_key, i)
                            with winreg.OpenKey(reg_key, app_key_name) as app_key:
                                app = self.get_app_info(app_key)
                                if app and not any(existing_app["name"] == app["name"] for existing_app in apps):
                                    apps.append(app)
                        except WindowsError:
                            continue
            except FileNotFoundError:
                continue

        return sorted(apps, key=lambda x: x["name"].lower())

    def get_app_info(self, app_key):
        try:
            name = winreg.QueryValueEx(app_key, "DisplayName")[0]
            try:
                size_kb = winreg.QueryValueEx(app_key, "EstimatedSize")[0]
            except FileNotFoundError:
                size_kb = 0
            try:
                install_date = winreg.QueryValueEx(app_key, "InstallDate")[0]
            except FileNotFoundError:
                install_date = None

            return {
                "name": name,
                "size": self.format_size(size_kb * 1024),
                "size_bytes": size_kb * 1024,
                "installed_on": self.format_date(install_date)
            }
        except FileNotFoundError:
            return None

    @staticmethod
    def format_size(size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def format_date(date_str):
        if not date_str:
            return "Unknown"
        try:
            return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
        except ValueError:
            return "Unknown"

    def update_loaded_info(self):
        count = len(self.installed_apps)
        total_size = sum(app["size_bytes"] for app in self.installed_apps)
        self.loaded_info_label.configure(text=f"Loaded {count} programs, total {self.format_size(total_size)}")

    def sort_column(self, col):
        self.sort_order[col] = not self.sort_order[col]
        reverse = not self.sort_order[col]

        if col == "Name":
            self.installed_apps.sort(key=lambda x: x["name"].lower(), reverse=reverse)
        elif col == "Size":
            self.installed_apps.sort(key=lambda x: x["size_bytes"], reverse=reverse)
        elif col == "Installed On":
            self.installed_apps.sort(key=lambda x: x["installed_on"], reverse=reverse)

        self.update_treeview()

    def show_context_menu(self, event):
        item = self.treeview.identify_row(event.y)
        if item:
            self.treeview.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def uninstall_selected(self):
        selected_item = self.treeview.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select an application to uninstall.")
            return

        app_name = self.treeview.item(selected_item, "values")[0]
        uninstall_cmd = self.get_uninstall_command(app_name)

        if not uninstall_cmd:
            messagebox.showerror("Error", f"Uninstall command for {app_name} not found.")
            return

        if messagebox.askyesno("Confirm Uninstall", f"Are you sure you want to uninstall {app_name}?"):
            try:
                subprocess.Popen(uninstall_cmd, shell=True)
                messagebox.showinfo("Uninstall Initiated",
                                    f"Uninstall process for {app_name} has been initiated. Please follow any on-screen instructions to complete the uninstallation.")
                self.refresh_apps()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to uninstall {app_name}: {e}")

    def get_uninstall_command(self, app_name):
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for reg_root, reg_path in reg_paths:
            try:
                with winreg.OpenKey(reg_root, reg_path) as reg_key:
                    for i in range(winreg.QueryInfoKey(reg_key)[0]):
                        try:
                            app_key_name = winreg.EnumKey(reg_key, i)
                            with winreg.OpenKey(reg_key, app_key_name) as app_key:
                                if winreg.QueryValueEx(app_key, "DisplayName")[0] == app_name:
                                    return winreg.QueryValueEx(app_key, "UninstallString")[0]
                        except WindowsError:
                            continue
            except FileNotFoundError:
                continue

        return None

    def refresh_apps(self):
        self.fetch_data()

    def check_for_updates(self):
        threading.Thread(target=self._check_for_updates, daemon=True).start()

    def _check_for_updates(self):
        repo_owner = 'LupuC'
        repo_name = 'elixio_uninstaller'
        url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest'

        try:
            response = requests.get(url)
            response.raise_for_status()
            release_info = response.json()
            latest_version = release_info['tag_name']

            if latest_version != self.config['version']:
                self.root.after(0, self.prompt_update, latest_version)
        except requests.RequestException as e:
            print(f"Failed to check for updates: {e}")

    def prompt_update(self, latest_version):
        if messagebox.askyesno("Update Available",
                               f"New version available: {latest_version}\n"
                               f"Current version: {self.config['version']}\n\n"
                               "Do you want to update now?"):
            self.download_update()

    def download_update(self):
        repo_owner = 'LupuC'
        repo_name = 'elixio_uninstaller'
        base_url = f'https://github.com/{repo_owner}/{repo_name}/releases/latest/download/'
        files_to_download = ['elixio_uninstaller.exe', 'config.json']

        try:
            for file in files_to_download:
                url = base_url + file
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(file, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)

            messagebox.showinfo("Update Successful", "Update downloaded successfully. Please restart the application.")
            self.root.quit()
        except requests.RequestException as e:
            messagebox.showerror("Download Error", f"Failed to download update: {e}")

    def run(self):
        self.root.mainloop()


class LoadingIndicator(customtkinter.CTkLabel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.characters = ['|', '/', '-', '\\']
        self.index = 0
        self.is_animating = False

    def start(self):
        self.is_animating = True
        self.animate()

    def stop(self):
        self.is_animating = False
        self.configure(text="")

    def animate(self):
        if self.is_animating:
            self.configure(text=self.characters[self.index])
            self.index = (self.index + 1) % len(self.characters)
            self.after(100, self.animate)


if __name__ == "__main__":
    app = ElixioUninstaller()
    app.run()