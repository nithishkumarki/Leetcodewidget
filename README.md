# LeetCode Desktop Widget 🚀

A native, interactive Windows desktop widget built using **Python** and **PyQt6** that displays your live LeetCode stats, streak metrics, and GitHub-style submission heatmap directly on your desktop wallpaper.

---

## ✨ Features
- **Live LeetCode Sync:** Fetches real-time stats via LeetCode's GraphQL API (Total Solved, Easy/Medium/Hard breakdown).
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
Ensure you have Python (3.8 or higher) installed on your Windows machine.

### 2. Install Dependencies
Open your terminal (Command Prompt or PowerShell) and run:
```bash
pip install PyQt6 requests


3. Configure Your Widget
Open the script file and update your personal settings at the top:

Python
LEETCODE_USERNAME = "your_leetcode_username"
IMAGE_PATH = r"C:\Path\To\Your\Wallpaper.jpg"
🚀 Run Automatically on Windows Startup (Shortcut Guide)
To make your widget open automatically every time you turn on your PC:

Create a Shortcut of your Script:

Right-click your widget.py file.

Select Show more options > Create shortcut.

Open the Windows Startup Folder:

Press Windows Key + R to open the Run dialog.

Type shell:startup and press Enter. (This opens the system Startup folder).

Move the Shortcut:

Drag and drop the shortcut you created in Step 1 into the shell:startup folder.

(Optional) Right-click the shortcut in the Startup folder, go to Properties, and under the Run dropdown, you can select Minimized if desired.
