import requests
import shutil
import threading
import sys
import subprocess
from tkinter import messagebox


class Updater:
    def __init__(self, current_version: str):
        self.current_version = current_version
        self.repo_owner = 'LupuC'
        self.repo_name = 'elixio_uninstaller'
        self.api_url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest'

    def check_for_updates(self, root, prompt_update):
        threading.Thread(target=self._check_for_updates, args=(root, prompt_update), daemon=True).start()

    def _check_for_updates(self, root, prompt_update):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            release_info = response.json()
            latest_version = release_info['tag_name']

            if latest_version != self.current_version:
                root.after(0, prompt_update, latest_version)
        except requests.RequestException as e:
            print(f"Failed to check for updates: {e}")

    def download_update(self, quit_callback):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            release_info = response.json()

            # Download new executable
            exe_asset = next((asset for asset in release_info['assets'] if asset['name'] == 'elixio_uninstaller.exe'),
                             None)
            if exe_asset:
                download_url = exe_asset['browser_download_url']
                response = requests.get(download_url, stream=True)
                response.raise_for_status()
                new_exe_path = 'elixio_uninstaller_new.exe'
                with open(new_exe_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
            else:
                raise Exception("Executable not found in release assets")

            # Download new config.json
            config_url = f'https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/config.json'
            response = requests.get(config_url)
            response.raise_for_status()
            with open('config_new.json', 'wb') as f:
                f.write(response.content)

            messagebox.showinfo("Update Successful",
                                "Update downloaded successfully. The application will now restart.")

            # Create a batch file to replace the old exe and config, then start the new exe
            with open('update.bat', 'w') as batch_file:
                batch_file.write('@echo off\n')
                batch_file.write('timeout /t 1 /nobreak >nul\n')
                batch_file.write(f'move /y "{new_exe_path}" "{sys.executable}"\n')
                batch_file.write('move /y config_new.json config.json\n')
                batch_file.write(f'start "" "{sys.executable}"\n')
                batch_file.write('del "%~f0"\n')

            # Run the batch file and exit the current instance
            subprocess.Popen('update.bat', shell=True)
            quit_callback()

        except requests.RequestException as e:
            messagebox.showerror("Download Error", f"Failed to download update: {e}")
        except Exception as e:
            messagebox.showerror("Update Error", f"An error occurred during the update: {e}")