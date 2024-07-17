import json

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"

    def load_config(self):
        try:
            with open(self.config_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            default_config = {"version": "1.0.0"}
            self.save_config(default_config)
            return default_config

    def save_config(self, config):
        with open(self.config_file, "w") as file:
            json.dump(config, file)

    def get_color_scheme(self, is_dark_mode: bool) -> dict:
        if is_dark_mode:
            return {
                "bg": "#2E2E2E",
                "fg": "#FFFFFF",
                "button": "#3A3A3A",
                "accent": "#4A90E2"
            }
        else:
            return {
                "bg": "#FFFFFF",
                "fg": "#000000",
                "button": "#E0E0E0",
                "accent": "#007ACC"
            }

    @staticmethod
    def format_size(size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
