# 🖱️ Super Clicker

**Super Clicker** is a customizable Python-based autoclicker GUI application that records mouse click intervals and replays them with precision. Designed with usability and clarity in mind, it features dark mode styling, configurable keybinds, and a clean two-column layout.

---

## Features

### Intelligent Clicking
- Records **natural click intervals** (using left mouse button)
- Click playback is **timed** using the intervals you recorded
- Option to **loop playback** continuously

### Recording
- Pop-up interface to start/stop click recording
- Clicks are timestamped, and intervals are calculated live

### Save / Load
- Save recorded intervals to a `.txt` file (each line = seconds between clicks)
- Load previously recorded `.txt` files
- Helpful file dialogs included
- Sample intervals in the text file:
```
0.09031391143798828
0.11686491966247559
0.08239459991455078
0.10226178169250488
0.06230020523071289
0.13074588775634766
0.18714308738708496
0.07404637336730957
0.12333536148071289
0.09613537788391113
```

### Keybind Control
- **Toggle key**: Start or stop the autoclicker
- **Kill key**: Immediately exit the program
- Keybinds are set from a dedicated window
- Prevents duplicate bindings and shows current keys live

### Clean GUI Layout
- Dark gray background with white text
- **Two-column layout**:
  - Left: Loop toggle, click status, activity status, keybind display
  - Right: Record, Save, Load, Keybinds
- Hover styling removed for checkboxes for a clean look

### Custom Icon (optional)
- Add a file named `icon.ico` in the same directory
- Supported in executable builds

---
