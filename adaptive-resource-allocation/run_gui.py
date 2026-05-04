import tkinter as tk
from ui.main_window import MainWindow

def run_gui():
    root = tk.Tk()
    app = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
