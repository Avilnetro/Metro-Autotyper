import tkinter as tk
from tkinter import ttk
import pyautogui
import time
import keyboard  # For listening to hotkeys
import json  # For saving hotkeys to a file
import os

# File to store hotkeys
hotkey_file = "hotkeys.json"

# Default hotkeys
default_hotkeys = {
    "main_autotyper": "F5",
    "multi_typer": "F9"
}

# Load or create hotkeys
def load_hotkeys():
    """Loads hotkeys from file or sets defaults if missing."""
    if os.path.exists(hotkey_file):
        try:
            with open(hotkey_file, "r") as file:
                hotkeys = json.load(file)
                # Ensure all required keys exist
                for key, default in default_hotkeys.items():
                    if key not in hotkeys:
                        hotkeys[key] = default
                return hotkeys
        except (json.JSONDecodeError, IOError):
            pass  # If file is corrupted, use defaults

    # Save defaults if file is missing or corrupted
    save_hotkeys(default_hotkeys)
    return default_hotkeys

def save_hotkeys(hotkeys):
    """Saves hotkeys to JSON file."""
    with open(hotkey_file, "w") as file:
        json.dump(hotkeys, file, indent=4)

# Save window position
window_position_file = "window_position.json"

def save_window_position():
    """Save the current window position to a JSON file."""
    try:
        x = window.winfo_x()
        y = window.winfo_y()
        position = {"x": x, "y": y}

        with open(window_position_file, "w") as file:
            json.dump(position, file)
    except Exception as e:
        print(f"Error saving window position: {e}")

def load_window_position():
    """Load the last saved window position and apply it."""
    if os.path.exists(window_position_file):
        try:
            with open(window_position_file, "r") as file:
                position = json.load(file)
                x, y = position.get("x", 100), position.get("y", 100)  # Default to (100, 100)

                # Ensure the window is moved correctly across platforms
                window.geometry(f"+{x}+{y}")

        except Exception as e:
            print(f"Error loading window position: {e}")

# Variable to track if the countdown has started
countdown_started = False
stop_typing = False  # Flag to stop typing

# Human-typing mode flag
human_typing_enabled = False

# File path to store and load the last typed text
text_file_path = "last_text.txt"

# Function to update the countdown label every second
def update_countdown(count, first_run=True):
    global countdown_started

    # If stop was pressed, exit early and reset countdown
    if stop_typing:
        countdown_label.config(text="Typing stopped")
        countdown_started = False
        start_button.config(state="normal", bg="darkgreen")  # Reset Start button
        return

    # Only show countdown if this is the first run
    if first_run and count > 0:
        countdown_label.config(text=f"Typing in {count} seconds...")
        window.after(1000, lambda: update_countdown(count - 1, first_run))
    else:
        countdown_label.config(text="Typing...")

        def on_typing_complete():
            """Handles repeat logic or stops typing if repeat is disabled."""
            if repeat_enabled and not stop_typing:
                try:
                    repeat_interval = int(interval_entry.get()) * 1000  # Convert to milliseconds
                    window.after(repeat_interval, lambda: update_countdown(0, first_run=False))  # Skip countdown
                except ValueError:
                    countdown_label.config(text="Invalid interval. Please enter a valid number.")
            else:
                # Stop typing and reset UI if Repeat Mode is off
                stop_typing_action()

        if human_typing_enabled:
            simulate_human_typing(text_box.get("1.0", "end-1c"), on_typing_complete)
        else:
            pyautogui.write(text_box.get("1.0", "end-1c"))
            on_typing_complete()  # Immediately call repeat logic if not using human typing

# Function to simulate human typing (with delays)
def simulate_human_typing(text, callback=None):
    """Simulates human typing with an adjustable delay and calls a callback when finished."""
    try:
        delay_ms = max(5, int(wpm_entry.get()))  # Get user input in milliseconds (min 5ms)
    except ValueError:
        delay_ms = 20  # Default to 20ms if input is invalid

    def type_character(index=0):
        if stop_typing or index >= len(text):
            if callback:
                callback()  # Call repeat logic when typing is finished
            return  # Stop if typing is canceled or text is complete

        pyautogui.write(text[index])  # Type one character
        window.after(delay_ms, type_character, index + 1)  # Schedule next character

    type_character()  # Start typing

# Function to simulate typing the text from the textbox using pyautogui
def repeat_message():
    global stop_typing  # Make sure to access the global stop_typing flag
    if stop_typing:
        return  # Do nothing if typing is stopped

    if human_typing_enabled:
        simulate_human_typing(text_box.get("1.0", "end-1c"))
    else:
        pyautogui.write(text_box.get("1.0", "end-1c"))  # Simulate typing the message

    # If repeat is enabled, schedule the next repetition
    if repeat_enabled and not stop_typing:  # Check if repeat is enabled and typing is not stopped
        try:
            repeat_interval = int(interval_entry.get()) * 1000  # Convert seconds to milliseconds
            window.after(repeat_interval, repeat_message)  # Repeat after the specified interval
        except ValueError:
            countdown_label.config(text="Invalid interval. Please enter a valid number.")

# Function to toggle repeat behavior
def toggle_repeat():
    global repeat_enabled  # Global variable to track repeat status
    repeat_enabled = not repeat_enabled  # Toggle repeat mode
    # Update the button text based on repeat status
    if repeat_enabled:
        repeat_button.config(text="Repeat Enabled", bg="darkblue")  # Set to dark blue when enabled
    else:
        repeat_button.config(text="Repeat Disabled", bg="#171517")  # Set to carbon black when disabled

# Function to toggle human typing mode
def toggle_human_typing():
    global human_typing_enabled  # Global variable to track human typing mode status
    human_typing_enabled = not human_typing_enabled  # Toggle human typing mode
    if human_typing_enabled:
        human_typing_button.config(text="Human Typing Enabled", bg="darkblue")  # Set to dark blue when enabled
    else:
        human_typing_button.config(text="Human Typing Disabled", bg="#171517")  # Set to carbon black when disabled

# Function to start typing
def start_typing():
    global countdown_started  # Track whether the countdown has already been triggered
    global stop_typing  # Access the global stop_typing flag

    stop_typing = False
    start_button.config(state="disabled", bg="darkgreen")  # Dark green color when clicked
    stop_button.config(state="normal")  # Enable the Stop Typing button

    # Reset the countdown_started flag if typing was stopped
    if countdown_started:
        countdown_started = False

    # Trigger the countdown again if it's not already started
    if not countdown_started:  # Only trigger countdown once
        countdown_label.config(text="Starting countdown...")
        window.after(1000, update_countdown, 3)  # Start countdown from 3 seconds
        countdown_started = True  # Mark that the countdown has started

# Function to stop typing
def stop_typing_action():
    global stop_typing, countdown_started
    stop_typing = True
    countdown_started = False  # Reset countdown state

    start_button.config(state="normal", bg="darkgreen")  # Enable Start button
    stop_button.config(state="disabled", bg="darkred")  # Disable Stop button
    countdown_label.config(text="Typing stopped")  # Update UI


# Function to load the last typed text from the file
def load_last_text():
    if os.path.exists(text_file_path):
        with open(text_file_path, 'r') as file:
            text_box.insert(tk.END, file.read())  # Insert the text into the text box

# Function to save the current text to a file
def save_current_text():
    with open(text_file_path, 'w') as file:
        file.write(text_box.get("1.0", tk.END).strip())  # Save the text from the textbox

# Function to clear the text box
def clear_text():
    text_box.delete("1.0", tk.END)  # Clear the contents of the text box

# Function to copy selected text to the clipboard
def copy_to_clipboard(event=None):
    text = text_box.get("sel.first", "sel.last")
    window.clipboard_clear()
    window.clipboard_append(text)

# Function to cut selected text (copy + delete)
def cut_text(event=None):
    copy_to_clipboard()
    text_box.delete("sel.first", "sel.last")

# Function to select all text in the textbox
def select_all_text(event=None):
    text_box.tag_add("sel", "1.0", "end")

# Function to create the context menu
def create_context_menu(event):
    context_menu = tk.Menu(window, tearoff=0, bg="#171517", fg="white")
    context_menu.add_command(label="Cut", command=cut_text)
    context_menu.add_command(label="Copy", command=copy_to_clipboard)
    context_menu.add_command(label="Paste", command=lambda: text_box.insert(tk.END, window.clipboard_get()))
    context_menu.add_separator()
    context_menu.add_command(label="Select All", command=select_all_text)

    context_menu.post(event.x_root, event.y_root)
    # Bind a click event anywhere in the window to dismiss the context menu
    window.bind("<Button-1>", lambda e: context_menu.unpost())

# Create the main window
window = tk.Tk()  # Instantiate an instance of a window
window.geometry("600x800")  # Set window size (larger height to fit all elements)
window.title("Metro Autotyper")  # Set window title to "Metro Autotyper"

style = ttk.Style()
style.configure("TFrame", background="#171517")  # Carbon black background for frames

# Configure the Notebook widget (tabs container)
style.configure("TNotebook", background="#171517", borderwidth=0)
style.configure("TNotebook.Tab", background="#171517", foreground="white", padding=[10, 5], font=("Helvetica", 12))
style.map("TNotebook.Tab", background=[("selected", "#222222")])  # Darker gray when selected

# Create a Notebook (tab container)
tabs_container = ttk.Notebook(window)
tabs_container.pack(expand=True, fill="both")

# Create the "Main" tab
style = ttk.Style()
style.configure("TFrame", background="#171517")  # Set the background color

main_tab = ttk.Frame(tabs_container, style="TFrame")
tabs_container.add(main_tab, text="Main")

# Create additional tabs
multi_typer_tab = ttk.Frame(tabs_container, style="TFrame")
settings_tab = ttk.Frame(tabs_container, style="TFrame")

tabs_container.add(multi_typer_tab, text="Multi-Typer")
tabs_container.add(settings_tab, text="Settings")

# Allow the window to be resizable (both width and height)
window.resizable(True, True)

# Add an icon to the window
try:
    icon = tk.PhotoImage(file='lambda_blue.png')
    window.iconphoto(True, icon)
except Exception as e:
    print(f"Error loading icon: {e}")

# Prevent the window from resizing smaller than necessary to fit all content
window.pack_propagate(False)

# Set background color of the window to carbon black (#171517)
window.config(background="#171517")

# Create a Label to display the countdown timer
countdown_label = tk.Label(main_tab, text="", font=("Helvetica", 14), bg="#171517", fg="white")
countdown_label.pack(pady=10)

# Create a Frame to hold the Text widget and Scrollbar together
frame = tk.Frame(main_tab)
frame.pack(pady=20, expand=True, fill=tk.BOTH, padx=20)

# Create a Text widget (textbox) for typing a message
text_box = tk.Text(frame, height=12, width=50, bg="#171517", fg="white", font=("Helvetica", 12), insertbackground="white")
text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar to the Text widget
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_box.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Link the scrollbar to the text box
text_box.config(yscrollcommand=scrollbar.set)

# Customize the scrollbar style to match the background color (active and inactive states)
style = ttk.Style(main_tab)
style.configure("TScrollbar",
                gripcount=0,
                background="#171517",  # Set scrollbar color to match the background
                darkcolor="#171517",
                lightcolor="#171517",
                troughcolor="#171517",  # Ensure the trough (empty area) is the same color
                arrowcolor="white")

# Set the scrollbar when inactive (in its "trough" state) to match the background
style.map("TScrollbar",
          background=[('active', '#171517'), ('!active', '#171517')],
          troughcolor=[('active', '#171517'), ('!active', '#171517')])

# Bind right-click (Button-3) to the context menu
text_box.bind("<Button-3>", create_context_menu)

# Create the Clear Text Button (above the Repeat Toggle Button)
clear_button = tk.Button(main_tab, text="Clear Text", command=clear_text, bg="#171517", fg="white", font=("Helvetica", 12))
clear_button.pack(pady=5)

# Create a Button to toggle repeat mode
repeat_enabled = False  # Initial state is disabled
repeat_button = tk.Button(main_tab, text="Repeat Disabled", command=toggle_repeat, bg="#171517", fg="white", font=("Helvetica", 12))
repeat_button.pack(pady=10)

# Create a Textbox to input the interval (in seconds) for repeating the message
interval_label = tk.Label(main_tab, text="Repeat interval (seconds):", font=("Helvetica", 12), bg="#171517", fg="white")
interval_label.pack(pady=5)

interval_entry = tk.Entry(main_tab, width=10, font=("Helvetica", 12), bg="#171517", fg="white", insertbackground="white")  # Make the interval textbox charcoal with white text
interval_entry.insert(0, "1")  # Default value is 1 second
interval_entry.pack(pady=5)

# Human-typing Mode Control
human_typing_button = tk.Button(main_tab, text="Human Typing Disabled", command=toggle_human_typing, bg="#171517", fg="white", font=("Helvetica", 12))
human_typing_button.pack(pady=10)

wpm_label = tk.Label(main_tab, text="Typing Speed (ms per character):", font=("Helvetica", 12), bg="#171517", fg="white")
wpm_label.pack(pady=5)

wpm_entry = tk.Entry(main_tab, width=10, font=("Helvetica", 12), bg="#171517", fg="white", insertbackground="white")
wpm_entry.insert(0, "5")  # Default value is 5 ms
wpm_entry.pack(pady=5)

# Create the Start Typing Button (initially enabled)
start_button = tk.Button(main_tab, text="Start Typing", command=start_typing, bg="darkgreen", fg="white", font=("Helvetica", 12))
start_button.pack(pady=10)

# Create the Stop Typing Button (initially disabled)
stop_button = tk.Button(main_tab, text="Stop Typing", command=stop_typing_action, bg="darkred", fg="white", font=("Helvetica", 12), state="disabled")
stop_button.pack(pady=10)

# Multi-Typer Variables
multi_typing_started = False
stop_multi_typing = False
multi_typer_repeat_enabled = False  # Default: Repeat mode is off

# Function to update the countdown label for Multi-Typer
def update_multi_typing_countdown(count):
    global multi_typing_started

    # If stop was pressed, exit early and reset countdown
    if stop_multi_typing:
        multi_countdown_label.config(text="Multi-typing stopped")
        multi_typing_started = False
        return

    if count > 0:
        multi_countdown_label.config(text=f"Typing in {count} seconds...")
        window.after(1000, update_multi_typing_countdown, count - 1)
    else:
        multi_countdown_label.config(text="Typing...")
        if not stop_multi_typing:  # Double-check stop condition before typing
            start_multi_typing_sequence()

# Function to start multi-typing
def start_multi_typing():
    global stop_multi_typing, multi_typing_started

    if multi_typing_started:  # Prevent multiple countdowns running at once
        return

    stop_multi_typing = False
    multi_typing_started = True  # Mark typing as started
    start_multi_typing_button.config(state="disabled", bg="darkgreen")
    stop_multi_typing_button.config(state="normal", bg="darkred")

    multi_countdown_label.config(text="Starting countdown...")
    window.after(1000, update_multi_typing_countdown, 3)

# Function to stop multi-typing
def stop_multi_typing_action():
    global stop_multi_typing, multi_typing_started
    stop_multi_typing = True
    multi_typing_started = False  # Reset countdown state

    # Cancel any pending countdown updates
    window.after_cancel(update_multi_typing_countdown)

    start_multi_typing_button.config(state="normal", bg="darkgreen")  # Enable start button
    stop_multi_typing_button.config(state="disabled", bg="darkred")  # Disable stop button
    multi_countdown_label.config(text="Multi-typing stopped")  # Update UI

# Function to send messages in sequence with delay
def start_multi_typing_sequence():
    global stop_multi_typing

    messages = [box.get("1.0", "end-1c").strip() for box in multi_text_boxes if box.get("1.0", "end-1c").strip()]
    if not messages:
        multi_countdown_label.config(text="No messages to type.")
        return

    try:
        delay_between_messages = int(multi_interval_entry.get()) * 1000  # Convert seconds to milliseconds
    except ValueError:
        multi_countdown_label.config(text="Invalid interval. Enter a number.")
        return

    def send_messages(index=0):
        if stop_multi_typing:
            return  # Stop if user presses stop

        pyautogui.write(messages[index])  # Type the message
        pyautogui.press("enter")  # Simulate pressing Enter

        # Move to the next message or restart if repeat mode is enabled
        next_index = index + 1
        if next_index >= len(messages):  # If at the end of the list
            if multi_typer_repeat_enabled:
                next_index = 0  # Loop back to the first message
            else:
                return  # Stop if repeat is not enabled

        window.after(delay_between_messages, send_messages, next_index)  # Schedule next message

    send_messages()

# Function to toggle multi-typer repeat mode
def toggle_multi_typer_repeat():
    global multi_typer_repeat_enabled
    multi_typer_repeat_enabled = not multi_typer_repeat_enabled  # Toggle state

    # Update button appearance
    if multi_typer_repeat_enabled:
        multi_typer_repeat_button.config(text="Repeat Enabled", bg="darkblue")
    else:
        multi_typer_repeat_button.config(text="Repeat Disabled", bg="#171517")

# Multi-Typer UI Components
multi_countdown_label = tk.Label(multi_typer_tab, text="", font=("Helvetica", 14), bg="#171517", fg="white")
multi_countdown_label.pack(pady=10)

# Add Multi-Typer Text Boxes
multi_text_boxes = []
for i in range(5):
    box = tk.Text(multi_typer_tab, height=3, width=50, bg="#171517", fg="white",
                  font=("Helvetica", 12), insertbackground="white")
    box.pack(pady=5)
    multi_text_boxes.append(box)

# Repeat Toggle Button (Placed Below Text Boxes but Above Interval Input)
multi_typer_repeat_button = tk.Button(multi_typer_tab, text="Repeat Disabled",
                                      command=toggle_multi_typer_repeat,
                                      bg="#171517", fg="white", font=("Helvetica", 12))
multi_typer_repeat_button.pack(pady=10)

# Interval input for Multi-Typer
multi_interval_label = tk.Label(multi_typer_tab, text="Interval between messages (seconds):",
                                font=("Helvetica", 12), bg="#171517", fg="white")
multi_interval_label.pack(pady=5)

multi_interval_entry = tk.Entry(multi_typer_tab, width=10, font=("Helvetica", 12),
                                bg="#171517", fg="white", insertbackground="white")
multi_interval_entry.insert(0, "1")  # Default delay of 1 second
multi_interval_entry.pack(pady=5)

# Start Multi-Typing Button (Must Be Defined Before Using .pack())
start_multi_typing_button = tk.Button(multi_typer_tab, text="Start Multi-Typing",
                                      command=start_multi_typing, bg="darkgreen",
                                      fg="white", font=("Helvetica", 12))
start_multi_typing_button.pack(pady=10)

# Stop Multi-Typing Button
stop_multi_typing_button = tk.Button(multi_typer_tab, text="Stop Multi-Typing",
                                     command=stop_multi_typing_action, bg="darkred",
                                     fg="white", font=("Helvetica", 12), state="disabled")
stop_multi_typing_button.pack(pady=10)

# File path for Multi-Typer saved messages
multi_text_file_path = "last_text_multi.txt"

# Function to load last typed text in Multi-Typer
def load_last_multi_text():
    if os.path.exists(multi_text_file_path):
        with open(multi_text_file_path, 'r') as file:
            lines = file.readlines()
            for i in range(min(5, len(lines))):  # Ensure we don't exceed available text boxes
                multi_text_boxes[i].delete("1.0", tk.END)  # Clear previous content
                multi_text_boxes[i].insert(tk.END, lines[i].strip())  # Insert saved text

# Function to save current text in Multi-Typer
def save_current_multi_text():
    with open(multi_text_file_path, 'w') as file:
        for text_box in multi_text_boxes:
            file.write(text_box.get("1.0", tk.END).strip() + "\n")  # Save each message on a new line

# Load existing hotkeys or set defaults
hotkeys = load_hotkeys()

# Function to update hotkeys dynamically
def set_hotkey(hotkey_type, entry):
    global hotkeys
    new_hotkey = entry.get().strip()

    if new_hotkey:
        hotkeys[hotkey_type] = new_hotkey
        save_hotkeys(hotkeys)  # Save to file
        bind_hotkeys()  # Rebind hotkeys immediately

        # Show confirmation in UI
        countdown_label.config(text=f"Hotkey for {hotkey_type.replace('_', ' ').title()} set to {new_hotkey}")

# UI Elements for Hotkey Input
tk.Label(settings_tab, text="Main Autotyper Hotkey:", font=("Helvetica", 12), bg="#171517", fg="white").pack(pady=5)
main_autotyper_hotkey_entry = tk.Entry(settings_tab, width=10, font=("Helvetica", 12), bg="#171517", fg="white", insertbackground="white")
main_autotyper_hotkey_entry.insert(0, hotkeys["main_autotyper"])
main_autotyper_hotkey_entry.pack(pady=5)

set_main_autotyper_hotkey_button = tk.Button(settings_tab, text="Set Main Autotyper Hotkey",
                                             command=lambda: set_hotkey("main_autotyper", main_autotyper_hotkey_entry),
                                             bg="#171517", fg="white", font=("Helvetica", 12))
set_main_autotyper_hotkey_button.pack(pady=5)

tk.Label(settings_tab, text="Multi-Typer Hotkey:", font=("Helvetica", 12), bg="#171517", fg="white").pack(pady=5)
multi_typer_hotkey_entry = tk.Entry(settings_tab, width=10, font=("Helvetica", 12), bg="#171517", fg="white", insertbackground="white")
multi_typer_hotkey_entry.insert(0, hotkeys["multi_typer"])
multi_typer_hotkey_entry.pack(pady=5)

set_multi_typer_hotkey_button = tk.Button(settings_tab, text="Set Multi-Typer Hotkey",
                                          command=lambda: set_hotkey("multi_typer", multi_typer_hotkey_entry),
                                          bg="#171517", fg="white", font=("Helvetica", 12))
set_multi_typer_hotkey_button.pack(pady=5)

# Load the last typed text when the program starts
load_last_text()
load_last_multi_text()

# Save the text when the window is closed
window.protocol("WM_DELETE_WINDOW", lambda: (save_current_text(), save_current_multi_text(), window.quit()))

# Keep track of currently bound hotkeys
active_hotkeys = []

def bind_hotkeys():
    """Unbind existing hotkeys and bind new ones dynamically."""
    global active_hotkeys

    # Remove previously bound hotkeys
    for hotkey in active_hotkeys:
        keyboard.remove_hotkey(hotkey)
    active_hotkeys.clear()  # Reset the list

    hotkeys = load_hotkeys()  # Reload from file

    # Bind new hotkeys
    hotkey1 = keyboard.add_hotkey(hotkeys["main_autotyper"], lambda: start_typing() if start_button["state"] == "normal" else stop_typing_action())
    hotkey2 = keyboard.add_hotkey(hotkeys["multi_typer"], lambda: start_multi_typing() if start_multi_typing_button["state"] == "normal" else stop_multi_typing_action())

    active_hotkeys.extend([hotkey1, hotkey2])

# Ensure hotkeys are bound on startup
bind_hotkeys()

# Run the main event loop
window.protocol("WM_DELETE_WINDOW", lambda: (save_current_text(), save_current_multi_text(), save_window_position(), window.quit()))

load_window_position()  # Restore last window position
window.mainloop()  # Start main event loop
