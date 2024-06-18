import os
import sys
import subprocess
import configparser
import threading
import tkinter as tk
from tkinter import Toplevel, Text, Label, Button, Entry, messagebox, Scrollbar
from ttkthemes import ThemedStyle
import pyautogui
import webbrowser
import keyboard
import time

# Function to install Python packages
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    print(f"[UPDATE] Checking/Installing Your Package (Package: {package})")

# Display menu for package installation
def display_menu():
    print("[1] Auto Install Packages")
    print("[0] Continue Without Installing")
    option = int(input("Enter Your Option: "))
    if option == 1:
        install("tk")
        install("ttkthemes")
        install("keyboard")
        install("configparser")
    elif option == 0:
        print("[UPDATE] Continuing")
    else:
        print("Invalid Option.")
        display_menu()

# Configuration file setup
def setup_config():
    config = configparser.ConfigParser()
    config_path = os.path.join("Configs", "Config.ini")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    if os.path.isfile(config_path):
        print(f"[UPDATE] Config File Exists At Path: {os.path.abspath(config_path)}")
    else:
        print("[WARNING] Config File Not Found. Creating Now...")
        config['HotKeys'] = {
            'record': 'f',
            'start': 'r',
            'stop': 'd'
        }
        with open(config_path, 'w') as config_file:
            config.write(config_file)
        print(f"[UPDATE] Config File Created At: {os.path.abspath(config_path)}")

    return config_path, config

# SnapBot class for handling auto-clicking functionality
class SnapBot:
    def __init__(self):
        self.running = False
        self.click_positions = []
        self.delays = []
        self.hotkeys = {}

    def start_clicking(self):
        self.running = True
        while self.running:
            for pos, delay in zip(self.click_positions, self.delays):
                pyautogui.moveTo(pos)
                pyautogui.click(pos)
                time.sleep(delay)
                if not self.running:
                    break

    def start(self):
        if self.click_positions:
            threading.Thread(target=self.start_clicking).start()
            print("[UPDATE] Auto clicker started.")
        else:
            print("[WARNING] Please record at least one position before starting auto-clicker.")

    def stop(self):
        self.running = False
        print("[UPDATE] Auto clicker stopped.")

    def record_position(self, delay):
        position = pyautogui.position()
        self.click_positions.append(position)
        self.delays.append(delay)
        update_positions_text()
        print(f"[UPDATE] Recorded position: {position} with delay {delay} seconds")

    def update_delay(self, index, new_delay):
        self.delays[index] = new_delay
        update_positions_text()
        print(f"[UPDATE] Updated delay for position {index + 1} to {new_delay} seconds")

# GUI functions
def update_positions_text():
    positions_text.delete(1.0, tk.END)
    for index, (pos, delay) in enumerate(zip(snapbot.click_positions, snapbot.delays)):
        positions_text.insert(tk.END, f"{index + 1}. ({pos[0]}, {pos[1]}) - Delay: {delay}s\n")

def clear_positions():
    if messagebox.askyesno("Clear Positions", "Are you sure you want to clear all positions?"):
        snapbot.click_positions = []
        snapbot.delays = []
        update_positions_text()
        print("[UPDATE] Cleared positions.")

def toggle_auto_clicker():
    try:
        delay = float(delay_input.get())
        if delay <= 0:
            raise ValueError
        snapbot.record_position(delay)
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid positive delay time.")

def start_stop_auto_clicker():
    if snapbot.running:
        snapbot.stop()
    else:
        snapbot.start()

def open_github():
    webbrowser.open("https://github.com/Dartedd/snapscore/blob/main/")

def open_discord():
    webbrowser.open("https://discord.gg/h482AtAQ7X")

def change_hotkeys_window():
    hotkeys_window = Toplevel(window)
    hotkeys_window.title("Change Hotkeys")
    hotkeys_window.geometry("300x200")

    for action in snapbot.hotkeys:
        label = Label(hotkeys_window, text=f"Change {action.capitalize()} Key")
        label.pack()
        entry_var = tk.StringVar(value=snapbot.hotkeys[action])  # Use StringVar to hold current hotkey
        entry = tk.Entry(hotkeys_window, textvariable=entry_var)
        entry.pack()

        def update_and_save(action=action, entry_var=entry_var):
            new_hotkey = entry_var.get()
            snapbot.hotkeys[action] = new_hotkey
            config.set("HotKeys", action, new_hotkey)
            with open(config_path, "w") as config_file:
                config.write(config_file)
            print(f"[UPDATE] Hotkey for {action} changed to {new_hotkey}")

        button = Button(hotkeys_window, text="Change", command=update_and_save)
        button.pack(pady=5)

def open_edit_delay_window(index):
    edit_window = Toplevel(window)
    edit_window.title(f"Edit Delay for Position {index + 1}")
    edit_window.geometry("300x150")
    edit_window.resizable(False, False)

    style = ThemedStyle(edit_window)
    style.theme_use('equilux')

    main_frame = tk.Frame(edit_window, bg="#303030")
    main_frame.pack(fill=tk.BOTH, expand=True)

    Label(main_frame, text=f"Current Delay: {snapbot.delays[index]} seconds", bg="#303030", fg="#FFFFFF").pack(pady=10)

    new_delay_entry = Entry(main_frame, width=10, font=("Arial", 10))
    new_delay_entry.pack(pady=5)
    new_delay_entry.insert(0, snapbot.delays[index])

    def update_delay():
        try:
            new_delay = float(new_delay_entry.get())
            if new_delay <= 0:
                raise ValueError
            snapbot.update_delay(index, new_delay)
            edit_window.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive delay time.")

    update_button = Button(main_frame, text="Update", width=10, bg="#212121", fg="#FFFFFF", command=update_delay, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
    update_button.pack(pady=10)
    update_button.bind("<Enter>", lambda event: update_button.config(bg="#333333"))
    update_button.bind("<Leave>", lambda event: update_button.config(bg="#212121"))

    def on_close():
        edit_window.destroy()

    edit_window.protocol("WM_DELETE_WINDOW", on_close)

# Main application setup
if __name__ == "__main__":
    display_menu()
    config_path, config = setup_config()
    config.read(config_path)

    snapbot = SnapBot()
    snapbot.hotkeys = dict(config['HotKeys'])

    keyboard.add_hotkey(snapbot.hotkeys['record'], toggle_auto_clicker)
    keyboard.add_hotkey(snapbot.hotkeys['start'], start_stop_auto_clicker)

    # Load GUI
    window = tk.Tk()
    window.title("Snapscore booster")
    window.geometry("650x500")
    window.resizable(False, False)
    window.configure(bg="#303030")

    style = ThemedStyle(window)
    style.theme_use('equilux')

    positions_text = Text(window, height=14, width=60, font=("Arial", 10), bg="#505050", fg="#FFFFFF", insertbackground="#FFFFFF")
    positions_text.place(x=20, y=150)

    Label(window, text="Enter Delay for Next Click (seconds):", bg="#303030", fg="#FFFFFF").place(x=20, y=40)
    delay_input = tk.Entry(window, width=10)
    delay_input.place(x=250, y=40)
    delay_input.insert(0, "0.5")

    description_label = tk.Label(window, text="you can click on the delay after recording to change it after ", wraplength=560, justify="left", bg="#303030", fg="#FFFFFF")
    description_label.place(x=20, y=100)

    def on_hover_enter(event):
        event.widget.config(bg="#333333")

    def on_hover_leave(event):
        event.widget.config(bg="#212121")

    def edit_position_delay(event):
        try:
            index = int(positions_text.index(tk.CURRENT).split('.')[0]) - 1
            open_edit_delay_window(index)
        except ValueError:
            pass

    positions_text.bind("<Double-1>", edit_position_delay)

    record_button = Button(window, text=f"Record ({snapbot.hotkeys['record']})", width=15, bg="#212121", fg="#FFFFFF", command=toggle_auto_clicker, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
    record_button.place(x=20, y=80)
    record_button.bind("<Enter>", on_hover_enter)
    record_button.bind("<Leave>", on_hover_leave)

    start_stop_button = Button(window, text=f"Start/Stop ({snapbot.hotkeys['start']})", width=15, bg="#212121", fg="#FFFFFF", command=start_stop_auto_clicker, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
    start_stop_button.place(x=150, y=80)
    start_stop_button.bind("<Enter>", on_hover_enter)
    start_stop_button.bind("<Leave>", on_hover_leave)

    clear_button = Button(window, text="Clear Positions", width=15, bg="#212121", fg="#FFFFFF", command=clear_positions, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
    clear_button.place(x=280, y=80)
    clear_button.bind("<Enter>", on_hover_enter)
    clear_button.bind("<Leave>", on_hover_leave)

    hotkeys_button = Button(window, text="Change HotKeys (restart after)", width=30, bg="#212121", fg="#FFFFFF", command=change_hotkeys_window, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
    hotkeys_button.place(x=410, y=80)
    hotkeys_button.bind("<Enter>", on_hover_enter)
    hotkeys_button.bind("<Leave>", on_hover_leave)

    github_button = Button(window, text="GitHub", width=10, bg="#212121", fg="#FFFFFF", command=open_github, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
    github_button.place(x=20, y=450)
    github_button.bind("<Enter>", on_hover_enter)
    github_button.bind("<Leave>", on_hover_leave)

    discord_button = Button(window, text="Discord", width=10, bg="#212121", fg="#FFFFFF", command=open_discord, borderwidth=0, highlightthickness=0, relief=tk.FLAT)
    discord_button.place(x=110, y=450)
    discord_button.bind("<Enter>", on_hover_enter)
    discord_button.bind("<Leave>", on_hover_leave)

    window.mainloop()


