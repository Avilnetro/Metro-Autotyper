# Metro Autotyper

**Metro Autotyper** is a simple Python GUI program that allows the user to automate typing tasks in a variety of ways. I decided to create this program as I felt most other autotypers were either lacking in features, or weren't behaving the way I needed them to.

## Features
- **Message looping/repeating mode** - repeat the same input for as long as you want, with adjustable delay
- **Human-typing mode** - toggle between instant text entry or simulated typing, with adjustable speed
- **Multi-typer** - send up to 5 unique messages in chronological order, loopable
- **Configurable hotkeys** - Bound to F5 (start autotyper) and F9 (start multi-typer) by default, can be changed in settings

## Screenshots
<img src="https://github.com/user-attachments/assets/d5ed191e-81ad-49f8-a278-4a40b2907478" height="500"/> <img src="https://github.com/user-attachments/assets/739acf17-c95f-48a0-b460-7bfde8bde004" height="500"/>

## Installation
Be sure to have the following dependencies:<br/>
Python 3<br/>
pyautogui<br/>
keyboard<br/>
<br/>
Extract anywhere and open metro-autotyper.py 

### Arch Linux:
`yay -S python-pyautogui python-keyboard`

### Windows 10:
`pip install pyautogui keyboard`

## Usage
`python metro-autotyper.py`

(sudo permissions required on Linux for hotkeys to work)
<br/>
<br/>
<br/>
Tested on: Arch Linux (Wayland), Windows 10.
