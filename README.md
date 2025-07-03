# 🖱️ Super Clicker

**Super Clicker** is a customizable Python-based autoclicker application that records mouse click intervals and replays them. Designed with usability and simplicity in mind, it features dark mode styling, configurable keybinds, and a clean two-column layout.

---

## Features

### Intelligent Clicking
- Records **natural click intervals** (using left mouse button)
- Click playback is **timed** using the intervals you recorded
- Option to **loop playback** continuously
- Can't record new clicks if there are already clicks loaded

### Recording
- Pop-up interface to start/stop click recording
- Clicks are timestamped, and intervals are calculated live

### Save / Load
- Save recorded intervals to a `.txt` file (each line = seconds between clicks)
- Load previously recorded `.txt` files
- Option to clear loaded files
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
...
```

### Keybinds
- **Toggle key**: Start or stop clicking
- **Kill key**: Immediately exit the program

### Custom Icon (optional)
- Add a file named `icon.ico` in the same directory
- Supported in executable builds

---
