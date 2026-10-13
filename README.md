# LeetCode Desktop Widget 🚀

A native, interactive Windows desktop widget built using Python and PyQt6 that displays your live LeetCode stats, streak metrics, and a GitHub-style submission heatmap directly on your desktop.

---

## ✨ Features
- **Live LeetCode Sync:** Fetches real-time stats via LeetCode's GraphQL API (total solved, easy/medium/hard breakdown).
- **Activity Heatmap:** Renders a GitHub-style 53-week submission calendar grid.
- **Custom Wallpaper Integration:** Blends smoothly over any custom background image with dark glassmorphism styling.
- **Interactive Windows Controls:**
  - Frameless, translucent window with drop shadow.
  - Drag anywhere to reposition.
  - Resize seamlessly from any corner or edge.
  - Right-click context menu to refresh stats, toggle "Always on Top", or quit.
- **Persistent State:** Remembers your custom window size and position across reboots.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.8 or higher installed on your Windows machine.

### 2. Install Dependencies
Open your terminal (Command Prompt or PowerShell) and run:

```bash
pip install PyQt6 requests
```

### 3. Configure Your Widget
Open the script file and update your personal settings at the top:

```python
LEETCODE_USERNAME = "your_leetcode_username"
IMAGE_PATH = r"C:\Path\To\Your\Wallpaper.jpg"
```

### 4. Run the Widget
From the project folder, run:

```bash
python widget.py
```

---

## 🚀 Run Automatically on Windows Startup
To make the widget open automatically every time you turn on your PC:

1. Right-click your `widget.py` file.
2. Select **Show more options > Create shortcut**.
3. Press `Windows + R`, type `shell:startup`, and press Enter.
4. Drag the shortcut into the Startup folder.

Optional: In the Startup folder, right-click the shortcut, open **Properties**, and set **Run** to **Minimized** if desired.
