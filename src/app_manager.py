import winreg
import threading
from datetime import datetime

class AppManager:
    def __init__(self):
        self.installed_apps = []


    def fetch_data(self, update_treeview): # def fetch_data(self, update_progress, update_treeview):
        def fetch():
            apps = self.get_installed_apps()
            self.installed_apps = apps
            #update_progress(1)
            update_treeview()

        threading.Thread(target=fetch, daemon=True).start()

    def get_installed_apps(self) -> list:
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
                                app_info = self.get_app_info(app_key)
                                if app_info:
                                    apps.append(app_info)
                        except FileNotFoundError:
                            continue
            except FileNotFoundError:
                continue

        return sorted(apps, key=lambda x: x["name"].lower())

    def get_app_info(self, app_key) -> dict:
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
    def format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def format_date(date_str: str) -> str:
        if not date_str:
            return "Unknown"
        try:
            return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
        except ValueError:
            return "Unknown"

    def sort_apps(self, col: str, reverse: bool):
        if col == "Name":
            self.installed_apps.sort(key=lambda x: x["name"].lower(), reverse=reverse)
        elif col == "Size":
            self.installed_apps.sort(key=lambda x: x["size_bytes"], reverse=reverse)
        elif col == "Installed On":
            self.installed_apps.sort(key=lambda x: x["installed_on"], reverse=reverse)

    def get_uninstall_command(self, app_name: str) -> str:
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
