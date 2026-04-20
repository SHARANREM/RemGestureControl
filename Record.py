import tkinter as tk
from tkinter import messagebox
from pynput import mouse, keyboard
import numpy as np
from pathlib import Path
import os

# ==============================
# SETTINGS
# ==============================

num_points = 64
tracking = False
positions = []
base_path = None
prefix = ""

ROOT_COLLECTION_FOLDER = Path("data/Collection")
ROOT_COLLECTION_FOLDER.mkdir(exist_ok=True)

# ==============================
# NORMALIZATION FUNCTION
# ==============================

def normalize_and_resample(pos_list):
    arr = np.array(pos_list)

    arr = arr - arr[0]

    max_val = np.max(np.abs(arr))
    if max_val != 0:
        arr = arr / max_val

    indices = np.linspace(0, len(arr) - 1, num_points).astype(int)
    arr = arr[indices]

    vectors = np.diff(arr, axis=0)

    return vectors.flatten()

# ==============================
# FILE NAMING
# ==============================

def get_next_filename():
    global base_path, prefix

    existing_files = [
        f for f in os.listdir(base_path)
        if f.startswith(prefix) and f.endswith(".npy")
    ]

    if not existing_files:
        return base_path / f"{prefix}1.npy"

    numbers = []
    for f in existing_files:
        try:
            num = int(f.replace(prefix, "").replace(".npy", ""))
            numbers.append(num)
        except:
            continue

    next_number = max(numbers) + 1 if numbers else 1
    return base_path / f"{prefix}{next_number}.npy"

# ==============================
# SAVE FUNCTION
# ==============================

def save_gesture(pos_list):
    feature_vector = normalize_and_resample(pos_list)
    filename = get_next_filename()
    np.save(filename, feature_vector)

    status_label.config(
        text=f"Saved: {filename.name}",
        fg="green"
    )

# ==============================
# MOUSE EVENTS
# ==============================

def on_move(x, y):
    global tracking, positions
    if tracking:
        positions.append((x, y))

def on_press(key):
    global tracking, positions
    if key == keyboard.Key.ctrl_l and not tracking:
        if base_path is None:
            status_label.config(text="Click Start First!", fg="red")
            return

        tracking = True
        positions = []
        status_label.config(text="Recording...", fg="blue")

def on_release(key):
    global tracking, positions
    if key == keyboard.Key.ctrl_l and tracking:
        tracking = False

        if len(positions) > 10:
            save_gesture(positions)
        else:
            status_label.config(text="Too few points", fg="red")

# ==============================
# START SETUP
# ==============================

def start_collection():
    global base_path, prefix

    gesture_name = gesture_entry.get().strip()

    if not gesture_name:
        messagebox.showerror("Error", "Please enter a Gesture Name.")
        return

    base_path = ROOT_COLLECTION_FOLDER / gesture_name
    base_path.mkdir(parents=True, exist_ok=True)

    # prefix = first letter OR full name (your choice)
    prefix = gesture_name[0].lower() + "_"

    status_label.config(
        text="Hold LEFT CTRL and draw gesture",
        fg="black"
    )

# ==============================
# TKINTER UI
# ==============================

root = tk.Tk()
root.title("Gesture Collector")
root.geometry("400x220")
root.resizable(False, False)

tk.Label(root, text="Gesture Name:", font=("Arial", 12)).pack(pady=10)
gesture_entry = tk.Entry(root, font=("Arial", 12))
gesture_entry.pack()

tk.Button(
    root,
    text="Start Collection",
    command=start_collection,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 12)
).pack(pady=15)

status_label = tk.Label(root, text="Waiting...", font=("Arial", 11))
status_label.pack(pady=10)

# ==============================
# START LISTENERS
# ==============================

mouse_listener = mouse.Listener(on_move=on_move)
keyboard_listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)

mouse_listener.start()
keyboard_listener.start()

root.mainloop()