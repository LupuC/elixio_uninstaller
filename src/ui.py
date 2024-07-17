import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter
from .config import ConfigManager
from .app_manager import AppManager
from .updater import Updater


class ElixioUninstaller:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.sort_order = {"Name": True, "Size": True, "Installed On": True}
        self.is_dark_mode = True
        self.colors = self.config_manager.get_color_scheme(self.is_dark_mode)
        self.app_manager = AppManager()
        self.updater = Updater(self.config['version'])
        self.init_ui()

    def init_ui(self):
        self.root = customtkinter.CTk()
        self.root.title("Elixio Uninstaller")
        self.root.geometry("600x800")

        customtkinter.set_appearance_mode("dark" if self.is_dark_mode else "light")
        customtkinter.set_default_color_theme("blue")

        self.create_main_frame()
        self.create_search_bar()
        self.create_treeview()
        self.create_info_bar()
        self.create_context_menu()
        self.create_buttons()

        self.updater.check_for_updates(self.root, self.prompt_update)
        self.fetch_data()

    def create_main_frame(self):
        self.main_frame = customtkinter.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def create_search_bar(self):
        search_frame = customtkinter.CTkFrame(self.main_frame)
        search_frame.pack(fill=tk.X, pady=10)

        search_label = customtkinter.CTkLabel(search_frame, text="Search apps:")
        search_label.pack(side=tk.LEFT, padx=10)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_search)
        search_entry = customtkinter.CTkEntry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def create_treeview(self):
        columns = ("Name", "Size", "Installed On")
        self.treeview = ttk.Treeview(self.main_frame, columns=columns, show="headings",
                                     style="Custom.Treeview", selectmode="extended")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                        background=self.colors["bg"],
                        foreground=self.colors["fg"],
                        fieldbackground=self.colors["bg"],
                        borderwidth=0,
                        rowheight=30)
        style.map('Custom.Treeview', background=[('selected', self.colors["accent"])])
        style.configure("Custom.Treeview.Heading",
                        background=self.colors["accent"],
                        foreground=self.colors["fg"],
                        relief="flat",
                        font=('Helvetica', 10, 'bold'))
        style.map("Custom.Treeview.Heading",
                  background=[('active', self.colors["bg"])])

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
        self.info_frame = customtkinter.CTkFrame(self.root, corner_radius=10)
        self.info_frame.pack(fill=tk.X, pady=10)

        self.loaded_info_label = customtkinter.CTkLabel(self.info_frame, text="Loading apps...")
        self.loaded_info_label.pack(side=tk.LEFT)

        # self.progress_bar = customtkinter.CTkProgressBar(self.info_frame, width=200)
        # self.progress_bar.pack(side=tk.LEFT, padx=10)
        # self.progress_bar.set(0)

        version_label = customtkinter.CTkLabel(self.info_frame, text=f"{self.config['version']}")
        version_label.pack(side=tk.RIGHT)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=False)
        self.context_menu.add_command(label="Uninstall", command=self.uninstall_selected)

    def create_buttons(self):
        button_frame = customtkinter.CTkFrame(self.root, corner_radius=10)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        refresh_button = customtkinter.CTkButton(button_frame, text="Refresh",
                                                 command=self.refresh_apps,
                                                 fg_color=self.colors["button"],
                                                 hover_color=self.colors["accent"])
        refresh_button.pack(side=tk.LEFT)

        uninstall_button = customtkinter.CTkButton(button_frame, text="Uninstall Selected",
                                                   command=self.uninstall_selected,
                                                   fg_color=self.colors["button"],
                                                   hover_color=self.colors["accent"])
        uninstall_button.pack(side=tk.LEFT, padx=5)

        mode_button = customtkinter.CTkButton(button_frame, text="Toggle Theme",
                                              command=self.toggle_theme,
                                              fg_color=self.colors["button"],
                                              hover_color=self.colors["accent"])
        mode_button.pack(side=tk.RIGHT)

    def update_search(self, *args):
        search_term = self.search_var.get().lower()
        self.treeview.delete(*self.treeview.get_children())
        for app in self.app_manager.installed_apps:
            if search_term in app["name"].lower():
                self.treeview.insert("", "end", values=(app["name"], app["size"], app["installed_on"]))

    def fetch_data(self):
        # self.progress_bar.set(0)
        # self.app_manager.fetch_data(self.update_progress, self.update_treeview)
        self.app_manager.fetch_data(self.update_treeview)


    #def update_progress(self, progress: float):
        # self.progress_bar.set(progress)

    def update_treeview(self):
        self.treeview.delete(*self.treeview.get_children())
        max_size_width = max(len(app["size"]) for app in self.app_manager.installed_apps)
        max_date_width = max(len(app["installed_on"]) for app in self.app_manager.installed_apps)

        self.treeview.column("Size", width=max_size_width * 10, )
        self.treeview.column("Installed On", width=max_date_width * 10)

        total_width = self.main_frame.winfo_width()
        name_width = total_width - (max_size_width * 10) - (max_date_width * 10) - 20
        self.treeview.column("Name", width=max(name_width, 200))

        for app in self.app_manager.installed_apps:
            self.treeview.insert("", "end", values=(app["name"], app["size"], app["installed_on"]))
        self.update_loaded_info()
        # self.progress_bar.set(1)

    def update_loaded_info(self):
        count = len(self.app_manager.installed_apps)
        total_size = sum(app["size_bytes"] for app in self.app_manager.installed_apps)
        self.loaded_info_label.configure(text=f"Loaded {count} programs, total {self.config_manager.format_size(total_size)}")

    def sort_column(self, col: str):
        self.sort_order[col] = not self.sort_order[col]
        reverse = not self.sort_order[col]

        self.app_manager.sort_apps(col, reverse)
        self.update_treeview()

    def show_context_menu(self, event):
        item = self.treeview.identify_row(event.y)
        if item:
            self.treeview.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def uninstall_selected(self):
        selected_items = self.treeview.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select application(s) to uninstall.")
            return

        app_names = [self.treeview.item(item, "values")[0] for item in selected_items]
        if messagebox.askyesno("Confirm Uninstall",
                               f"Are you sure you want to uninstall these {len(app_names)} application(s)?"):
            for app_name in app_names:
                uninstall_cmd = self.app_manager.get_uninstall_command(app_name)
                if uninstall_cmd:
                    try:
                        subprocess.Popen(uninstall_cmd, shell=True)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to uninstall {app_name}: {e}")

            messagebox.showinfo("Uninstall Initiated",
                                "Uninstall processes have been initiated. Please follow any on-screen instructions to complete the uninstallations.")
            self.refresh_apps()

    def refresh_apps(self):
        self.fetch_data()

    def prompt_update(self, latest_version: str):
        if messagebox.askyesno("Update Available",
                               f"New version available: {latest_version}\n"
                               f"Current version: {self.config['version']}\n\n"
                               "Do you want to update now?"):
            self.updater.download_update(self.root.quit)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        new_mode = "dark" if self.is_dark_mode else "light"
        customtkinter.set_appearance_mode(new_mode)
        self.colors = self.config_manager.get_color_scheme(self.is_dark_mode)
        self.update_colors()

    def update_colors(self):
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        background=self.colors["bg"],
                        foreground=self.colors["fg"],
                        fieldbackground=self.colors["bg"])
        style.map('Custom.Treeview', background=[('selected', self.colors["accent"])])
        style.configure("Custom.Treeview.Heading",
                        background=self.colors["accent"],
                        foreground=self.colors["fg"])
        style.map("Custom.Treeview.Heading",
                  background=[('active', self.colors["bg"])])

        for widget in [self.main_frame, self.info_frame]:
            widget.configure(fg_color=self.colors["bg"])

        for button in self.root.winfo_children():
            if isinstance(button, customtkinter.CTkButton):
                button.configure(fg_color=self.colors["button"], hover_color=self.colors["accent"])

        self.root.update()

    def run(self):
        self.root.mainloop()
