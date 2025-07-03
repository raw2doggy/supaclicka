import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, KeyCode
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
root.geometry("370x350")
loop_enabled = tk.BooleanVar()

# Status labels
status_label = ttk.Label(root, text="❌ No clicks recorded", foreground="red")
click_status_label = ttk.Label(root, text="🔴 Idle – not clicking", foreground="gray")

def update_status_label():
    if click_intervals:
        status_label.config(text="✅ Clicks recorded", foreground="green")
    else:
        status_label.config(text="❌ No clicks recorded", foreground="red")

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
        if isinstance(key, KeyCode):
            if key == toggle_key:
                toggle_clicking()
            elif key == kill_key:
                kill_program()

    global keyboard_listener
    keyboard_listener = Listener(on_press=on_press)
    keyboard_listener.start()

def open_keybind_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Keybind Settings")
    settings_window.geometry("300x200")
    settings_window.grab_set()

    tk.Label(settings_window, text="Press a key for TOGGLE:").pack(pady=5)
    toggle_label = tk.Label(settings_window, text="None", relief="sunken")
    toggle_label.pack()

    tk.Label(settings_window, text="Press a key for KILL:").pack(pady=5)
    kill_label = tk.Label(settings_window, text="None", relief="sunken")
    kill_label.pack()

    temp_keys = {'toggle': None, 'kill': None}

    def on_key_press(key):
        if not temp_keys['toggle']:
            temp_keys['toggle'] = key
            toggle_label.config(text=str(key))
        elif not temp_keys['kill']:
            temp_keys['kill'] = key
            kill_label.config(text=str(key))
        if temp_keys['toggle'] and temp_keys['kill']:
            return False

    def listen_for_keys():
        with keyboard.Listener(on_press=on_key_press) as listener:
            listener.join()

    def save_keys():
        nonlocal temp_keys
        global toggle_key, kill_key
        if temp_keys['toggle'] and temp_keys['kill']:
            toggle_key = temp_keys['toggle']
            kill_key = temp_keys['kill']
            messagebox.showinfo("Saved", f"Keybinds saved:\nToggle: {toggle_key}\nKill: {kill_key}")
            settings_window.destroy()
        else:
            messagebox.showerror("Error", "You must set both keybinds.")

    threading.Thread(target=listen_for_keys, daemon=True).start()
    ttk.Button(settings_window, text="Save & Close", command=save_keys).pack(pady=20)

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
ttk.Label(root, text="Use keybinds to toggle or kill").pack(pady=5)
ttk.Button(root, text="Exit", command=kill_program).pack(pady=10)

# Start threads
threading.Thread(target=click_loop, daemon=True).start()
start_keyboard_listener()
update_status_label()

# Launch GUI
root.mainloop()
