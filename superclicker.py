import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, Key, KeyCode
import os
import sys
import random

click_intervals = []
click_times = []

toggle_key = None
kill_key = None
clicking_enabled = False

mouse_controller = MouseController()
keyboard_listener = None
mouse_listener = None
keybind_menu_open = False

# GUI Setup
root = tk.Tk()
root.title("Super Clicker")
root.geometry("620x275")
root.configure(bg="#2e2e2e")

# Optional icon support
try:
    icon_path = os.path.join(sys._MEIPASS if hasattr(sys, "_MEIPASS") else ".", "icon.ico")
    root.iconbitmap(icon_path)
except Exception as e:
    print("Icon could not be set:", e)

loop_enabled = tk.BooleanVar()

# Dark theme style
style = ttk.Style()
style.theme_use('default')
style.configure('TLabel', background="#2e2e2e", foreground="white")
style.configure('TButton', background="#444444", foreground="white")
style.configure('TCheckbutton',
    background="#2e2e2e",
    foreground="white",
    focuscolor="",
    selectcolor="#2e2e2e"
)

style.map('TCheckbutton',
    background=[('active', '#2e2e2e'), ('selected', '#2e2e2e')],
    foreground=[('active', 'white'), ('selected', 'white')]
)


def update_status_label():
    if click_intervals:
        status_label.config(text="✅ Clicks loaded", foreground="green")
    else:
        status_label.config(text="❌ No clicks loaded", foreground="red")

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
    if click_intervals:
        messagebox.showwarning("Recording Disabled", "Cannot record new clicks while a file is loaded.\nClick 🧹 Clear Recording to enable.")
        return
    click_intervals.clear()
    click_times.clear()

    record_window = tk.Toplevel(root)
    record_window.title("Record Clicks")
    record_window.geometry("320x420")
    record_window.grab_set()
    record_window.configure(bg="#2e2e2e")

    info_label = tk.Label(record_window, text="Click the left mouse button to record\nClick in the box below to start.", bg="#2e2e2e", fg="white")
    info_label.pack(pady=10)

    # --- Recording mode selection ---
    mode_var = tk.StringVar(value="Unlimited")
    time_options = [("Unlimited", 0), ("15 seconds", 15), ("30 seconds", 30), ("45 seconds", 45), ("60 seconds", 60)]
    time_dropdown = ttk.Combobox(record_window, values=[opt[0] for opt in time_options], state="readonly", width=15)
    time_dropdown.current(0)
    time_dropdown.pack(pady=5)

    timer_label = tk.Label(record_window, text="", bg="#2e2e2e", fg="orange", font=("Segoe UI", 12, "bold"))
    timer_label.pack(pady=5)

    is_recording = tk.BooleanVar(value=False)
    clicks_recorded = tk.IntVar(value=0)
    recording_status_label = tk.Label(record_window, text="Status: Idle | Clicks: 0", bg="#2e2e2e", fg="lightblue")
    recording_status_label.pack(pady=5)

    marker_canvas = tk.Canvas(record_window, width=260, height=120, bg="#222", highlightthickness=1, highlightbackground="#444")
    marker_canvas.pack(pady=10)

    # Timer state
    timer_running = [False]
    timer_id = [None]
    start_time = [None]
    countdown_seconds = [0]

    def update_recording_status():
        status = "Recording..." if is_recording.get() else "Idle"
        recording_status_label.config(text=f"Status: {status} | Clicks: {clicks_recorded.get()}")

    def update_timer():
        if not is_recording.get():
            return
        mode = time_dropdown.get()
        now = time.time()
        if mode == "Unlimited":
            elapsed = int(now - start_time[0])
            timer_label.config(text=f"Elapsed: {elapsed}s")
            timer_id[0] = record_window.after(1000, update_timer)
        else:
            remaining = countdown_seconds[0] - int(now - start_time[0])
            if remaining >= 0:
                timer_label.config(text=f"Time left: {remaining}s")
                timer_id[0] = record_window.after(1000, update_timer)
            if remaining <= 0:
                stop_recording(timed_out=True)

    def place_marker(event):
        r = 5
        x, y = event.x, event.y
        marker_canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", outline="white")
        if not is_recording.get():
            start_listener()

    marker_canvas.bind("<Button-1>", place_marker)

    def on_click(x, y, button, pressed):
        if is_recording.get() and button == Button.left and pressed:
            now = time.time()
            click_times.append(now)
            clicks_recorded.set(clicks_recorded.get() + 1)
            update_recording_status()
            if len(click_times) > 1:
                interval = now - click_times[-2]
                click_intervals.append(interval)

    def start_listener():
        global mouse_listener, click_times, click_intervals
        if is_recording.get():
            return
        if mouse_listener:
            mouse_listener.stop()
            mouse_listener = None
        click_times.clear()
        click_intervals.clear()
        clicks_recorded.set(0)
        is_recording.set(True)
        update_recording_status()
        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()
        # Start timer
        start_time[0] = time.time()
        mode = time_dropdown.get()
        if mode == "Unlimited":
            timer_label.config(text="Elapsed: 0s")
            timer_running[0] = True
            update_timer()
        else:
            for name, seconds in time_options:
                if name == mode:
                    countdown_seconds[0] = seconds
                    break
            timer_label.config(text=f"Time left: {countdown_seconds[0]}s")
            timer_running[0] = True
            update_timer()

    def stop_recording(timed_out=False):
        global mouse_listener
        is_recording.set(False)
        update_recording_status()
        if timer_id[0]:
            record_window.after_cancel(timer_id[0])
            timer_id[0] = None
        if mouse_listener:
            mouse_listener.stop()
            mouse_listener = None
        update_status_label()
        loaded_file_label.config(text="📝 Cached clicks loaded")
        record_window.destroy()
        if timed_out:
            mode = time_dropdown.get()
            seconds = [s for n, s in time_options if n == mode][0]
            messagebox.showinfo("Recording Complete", f"{seconds} second recording is now loaded.")

    def on_close():
        global mouse_listener, click_times, click_intervals
        is_recording.set(False)
        if timer_id[0]:
            record_window.after_cancel(timer_id[0])
            timer_id[0] = None
        if mouse_listener:
            mouse_listener.stop()
            mouse_listener = None
        click_times.clear()
        click_intervals.clear()
        update_status_label()
        record_window.destroy()

    record_window.protocol("WM_DELETE_WINDOW", on_close)

    # --- Mode switching logic ---
    def on_mode_change(event=None):
        mode = time_dropdown.get()
        timer_label.config(text="")
        if is_recording.get():
            # If user changes mode while recording, stop and reset
            if timer_id[0]:
                record_window.after_cancel(timer_id[0])
                timer_id[0] = None
            is_recording.set(False)
            update_recording_status()
            if mouse_listener:
                mouse_listener.stop()
        if mode == "Unlimited":
            if not hasattr(record_window, "stop_btn"):
                record_window.stop_btn = ttk.Button(record_window, text="Stop Recording", command=stop_recording)
            record_window.stop_btn.pack(pady=5)
        else:
            if hasattr(record_window, "stop_btn"):
                record_window.stop_btn.pack_forget()

    time_dropdown.bind("<<ComboboxSelected>>", on_mode_change)
    on_mode_change()  # Set initial state


def click_loop():
    global clicking_enabled
    while True:
        if clicking_enabled and click_intervals:
            click_status_label.config(text="🟢 Clicking playback active...", foreground="green")

            for interval in click_intervals:
                if not clicking_enabled:
                    break
                
                # --- Randomness logic ---
                level = randomness_level.get()
                if level > 0:
                    # Each level is 10% chance, so level 5 = 50%
                    if random.random() < (level * 0.10):
                        # Randomly add or subtract 0.025s
                        delta = 0.025 if random.choice([True, False]) else -0.025
                        interval = max(0, interval + delta)
                # --- End randomness logic ---

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
        if keybind_menu_open:
            return  # Ignore keybinds while menu is open
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
    global keybind_menu_open
    keybind_menu_open = True
    settings_window = tk.Toplevel(root)
    settings_window.title("Keybind Settings")
    settings_window.geometry("320x270")
    settings_window.grab_set()
    settings_window.configure(bg="#2e2e2e")

    tk.Label(settings_window, text="Click a button to set a keybind:", bg="#2e2e2e", fg="white").pack(pady=10)

    toggle_label = tk.Label(settings_window, text="Toggle: None", relief="sunken", width=25, bg="white")
    toggle_label.pack(pady=5)
    kill_label = tk.Label(settings_window, text="Kill: None", relief="sunken", width=25, bg="white")
    kill_label.pack(pady=5)
    status_msg = tk.Label(settings_window, text="", foreground="lightblue", bg="#2e2e2e")
    status_msg.pack(pady=5)

    def wait_for_keybind(label_to_update, bind_type):
        status_msg.config(text="Press a key...")
        listener = None

        def on_press(key):
            nonlocal listener
            global toggle_key, kill_key
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
        global keybind_menu_open
        if toggle_key is None or kill_key is None:
            messagebox.showwarning("Incomplete", "Please set both keybinds.")
            return
        keybind_menu_open = False
        settings_window.destroy()

    ttk.Button(settings_window, text="Save & Close", command=close_window).pack(pady=15)

def save_intervals_to_file():
    if not click_intervals:
        messagebox.showwarning("Nothing to save", "There are no recorded intervals.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w") as f:
            for interval in click_intervals:
                f.write(f"{interval}\n")
        messagebox.showinfo("Saved", f"Saved to: {file_path}")

def load_intervals_from_file():
    global click_intervals
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path and os.path.exists(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
            click_intervals = [float(line.strip()) for line in lines if line.strip()]
        update_status_label()
        filename = os.path.basename(file_path)
        loaded_file_label.config(text=f"📂 Loaded from: {filename}")
        messagebox.showinfo("Loaded", f"Loaded {len(click_intervals)} intervals from {filename}.")

# Clear recordings
def clear_recording():
    global click_intervals
    if not click_intervals:
        messagebox.showinfo("Nothing to clear", "There are no recorded clicks to clear.")
        return
    click_intervals.clear()
    loaded_file_label.config(text="")
    update_status_label()


# Layout columns
left_frame = tk.Frame(root, bg="#2e2e2e")
right_frame = tk.Frame(root, bg="#2e2e2e")
left_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=30, pady=10)
right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=30, pady=10)

# Left column
ttk.Checkbutton(left_frame, text="Loop Playback", variable=loop_enabled).pack(pady=10)

# --- Randomness Level ---
randomness_level = tk.IntVar(value=0)
randomness_frame = tk.Frame(left_frame, bg="#2e2e2e")
randomness_frame.pack(pady=(0, 10))
ttk.Label(randomness_frame, text="Randomness Level:", background="#2e2e2e").pack(side=tk.LEFT, padx=(0, 5))
randomness_scale = ttk.Scale(randomness_frame, from_=0, to=5, orient=tk.HORIZONTAL, variable=randomness_level, length=120)
randomness_scale.pack(side=tk.LEFT)
randomness_value_label = ttk.Label(randomness_frame, textvariable=randomness_level, background="#2e2e2e")
randomness_value_label.pack(side=tk.LEFT, padx=(5, 0))
# --- End Randomness Level ---

status_label = ttk.Label(left_frame, text="❌ No clicks loaded", foreground="red", background="#2e2e2e")
status_label.pack(pady=(10, 0))

loaded_file_label = ttk.Label(left_frame, text="", foreground="lightgray", background="#2e2e2e", font=("Segoe UI", 9))
loaded_file_label.pack(pady=(0, 10))

click_status_label = ttk.Label(left_frame, text="🔴 Idle – not clicking", foreground="gray", background="#2e2e2e")
click_status_label.pack(pady=10)


keybind_status_label = ttk.Label(left_frame, text="Toggle: None | Kill: None", foreground="lightblue", background="#2e2e2e")
keybind_status_label.pack(pady=10)

# Right column
ttk.Button(right_frame, text="Record Clicks", command=start_click_recording_window).pack(pady=10)
ttk.Button(right_frame, text="💾 Save Recording", command=save_intervals_to_file).pack(pady=10)
ttk.Button(right_frame, text="📂 Load Recording", command=load_intervals_from_file).pack(pady=10)
ttk.Button(right_frame, text="🧹 Clear Recording", command=clear_recording).pack(pady=10)
ttk.Button(right_frame, text="Open Keybind Settings", command=open_keybind_window).pack(pady=10)

# Startup
threading.Thread(target=click_loop, daemon=True).start()
start_keyboard_listener()
update_status_label()
update_keybind_label()

root.mainloop()
