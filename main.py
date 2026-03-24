import tkinter as tk
from ui.launcher import LauncherWindow

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherWindow(root)
    root.mainloop()