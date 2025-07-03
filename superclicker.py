import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, Key, KeyCode
import os

click_intervals = []
click_times = []

toggle_key = None
kill_key = None
clicking_enabled = False

mouse_controller = MouseController()
keyboard_listener = None
mouse_listener = None

# GUI Setup
root = tk.Tk()
root.title("Autoclicker (Recorded Timing)")
root.geometry("370x420")
loop_enabled = tk.BooleanVar()

# Status labels
status_label = ttk.Label(root, text="❌ No clicks recorded", foreground="red")
click_status_label = ttk.Label(root, text="🔴 Idle – not clicking", foreground="gray")
keybind_status_label = ttk.Label(root, text="Toggle: None | Kill: None", foreground="blue")

def update_status_label():
    if click_intervals:
        status_label.config(text="✅ Clicks recorded", foreground="green")
    else:
        status_label.config(text="❌ No clicks recorded", foreground="red")

def update_keybind_label():
    global toggle_key, kill_key
    toggle_text = format_key(toggle_key) if toggle_key else "None"
    kill_text = format_key(kill_key) if kill_key else "None"
    keybind_status_label.config(text=f"Toggle: {toggle_text} | Kill: {kill_text}")

def format_key(key):
    if isinstance(key, KeyCode):
        return key.char or str(key)
    elif isinstance(key, Key):
        return key.name
    return str(key)

def start_click_recording_window():
    global click_times, click_intervals, mouse_listener
    click_intervals.clear()
    click_times.clear()

    record_window = tk.Toplevel(root)
    record_window.title("Record Clicks")
    record_window.geometry("300x160")
    record_window.grab_set()

    info_label = tk.Label(record_window, text="Click the left mouse button to record\nPress 'Stop Recording' to finish.")
    info_label.pack(pady=10)

    is_recording = tk.BooleanVar(value=False)

    def on_click(x, y, button, pressed):
        if is_recording.get() and button == Button.left and pressed:
            now = time.time()
            click_times.append(now)
            if len(click_times) > 1:
                interval = now - click_times[-2]
                click_intervals.append(interval)
                print(f"Recorded: {interval:.3f}s")

    def start_listener():
        global mouse_listener
        is_recording.set(True)
        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()

    def stop_recording():
        global mouse_listener
        is_recording.set(False)
        if mouse_listener:
            mouse_listener.stop()
            mouse_listener = None
        update_status_label()
        record_window.destroy()

    ttk.Button(record_window, text="Start Recording", command=start_listener).pack(pady=5)
    ttk.Button(record_window, text="Stop Recording", command=stop_recording).pack(pady=5)

def click_loop():
    global clicking_enabled
    while True:
        if clicking_enabled and click_intervals:
            click_status_label.config(text="🟢 Clicking playback active...", foreground="green")

            for interval in click_intervals:
                if not clicking_enabled:
                    break
                time.sleep(interval)
                mouse_controller.click(Button.left, 1)

            if not loop_enabled.get():
                clicking_enabled = False

            if not clicking_enabled:
                click_status_label.config(text="🔴 Idle – not clicking", foreground="gray")

        else:
            if click_status_label.cget("text") != "🔴 Idle – not clicking":
                click_status_label.config(text="🔴 Idle – not clicking", foreground="gray")

        time.sleep(0.05)

def toggle_clicking():
    global clicking_enabled
    clicking_enabled = not clicking_enabled
    print(f"Clicking {'enabled' if clicking_enabled else 'disabled'}")

def kill_program():
    print("Exiting program.")
    root.quit()

def start_keyboard_listener():
    def on_press(key):
        if toggle_key and keys_equal(key, toggle_key):
            toggle_clicking()
        elif kill_key and keys_equal(key, kill_key):
            kill_program()

    global keyboard_listener
    keyboard_listener = Listener(on_press=on_press)
    keyboard_listener.start()

def keys_equal(k1, k2):
    return format_key(k1).lower() == format_key(k2).lower()

def open_keybind_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Keybind Settings")
    settings_window.geometry("320x250")
    settings_window.grab_set()

    tk.Label(settings_window, text="Click a button to set a keybind:").pack(pady=10)

    toggle_label = tk.Label(settings_window, text="Toggle: None", relief="sunken", width=25)
    toggle_label.pack(pady=5)

    kill_label = tk.Label(settings_window, text="Kill: None", relief="sunken", width=25)
    kill_label.pack(pady=5)

    status_msg = tk.Label(settings_window, text="", foreground="blue")
    status_msg.pack(pady=5)

    def wait_for_keybind(label_to_update, bind_type):
        status_msg.config(text="Press a key...")
        listener = None

        def on_press(key):
            nonlocal listener
            global toggle_key, kill_key  # Moved here to be before use

            if bind_type == "Toggle" and keys_equal(key, kill_key):
                status_msg.config(text="❌ Already used for Kill!", foreground="red")
                return
            if bind_type == "Kill" and keys_equal(key, toggle_key):
                status_msg.config(text="❌ Already used for Toggle!", foreground="red")
                return

            key_str = format_key(key)
            label_to_update.config(text=f"{bind_type}: {key_str}")
            status_msg.config(text=f"{bind_type} set to: {key_str}", foreground="green")

            if bind_type == "Toggle":
                toggle_key = key
            elif bind_type == "Kill":
                kill_key = key

            update_keybind_label()
            if listener:
                listener.stop()


        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    ttk.Button(settings_window, text="Set TOGGLE Key", command=lambda: wait_for_keybind(toggle_label, "Toggle")).pack(pady=3)
    ttk.Button(settings_window, text="Set KILL Key", command=lambda: wait_for_keybind(kill_label, "Kill")).pack(pady=3)

    def close_window():
        if toggle_key is None or kill_key is None:
            messagebox.showwarning("Incomplete", "Please set both keybinds.")
            return
        settings_window.destroy()

    ttk.Button(settings_window, text="Save & Close", command=close_window).pack(pady=15)

def save_intervals_to_file():
    if not click_intervals:
        messagebox.showwarning("Nothing to save", "There are no recorded intervals.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt")],
                                             title="Save Click Intervals")
    if file_path:
        try:
            with open(file_path, "w") as f:
                for interval in click_intervals:
                    f.write(f"{interval}\n")
            messagebox.showinfo("Saved", f"Recording saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def load_intervals_from_file():
    global click_intervals
    file_path = filedialog.askopenfilename(defaultextension=".txt",
                                           filetypes=[("Text files", "*.txt")],
                                           title="Open Click Intervals")
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                click_intervals = [float(line.strip()) for line in lines if line.strip()]
            update_status_label()
            messagebox.showinfo("Loaded", f"Loaded {len(click_intervals)} intervals.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# GUI Widgets
ttk.Button(root, text="Record Clicks", command=start_click_recording_window).pack(pady=10)
ttk.Checkbutton(root, text="Loop Playback", variable=loop_enabled).pack()
ttk.Button(root, text="Open Keybind Settings", command=open_keybind_window).pack(pady=10)
ttk.Button(root, text="💾 Save Recording", command=save_intervals_to_file).pack(pady=2)
ttk.Button(root, text="📂 Load Recording", command=load_intervals_from_file).pack(pady=2)

status_label.pack(pady=5)
click_status_label.pack(pady=5)
keybind_status_label.pack(pady=5)

ttk.Label(root, text="Use keybinds to toggle or kill").pack(pady=5)
ttk.Button(root, text="Exit", command=kill_program).pack(pady=10)

# Start threads
threading.Thread(target=click_loop, daemon=True).start()
start_keyboard_listener()
update_status_label()
update_keybind_label()

# Launch GUI
root.mainloop()
