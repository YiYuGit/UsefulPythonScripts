import tkinter as tk
from tkinter import filedialog, messagebox  # Import the messagebox module
import os

def get_script_folder_path():
    script_path = os.path.realpath(__file__)
    folder_path = os.path.dirname(script_path)
    return folder_path

def display_folder_path():
    folder_path = get_script_folder_path()
    messagebox.showinfo("Folder Path", f"The current folder path is:\n\n{folder_path}")

root = tk.Tk()
root.title("Folder Path Finder")

button = tk.Button(root, text="Find Current Folder Path", command=display_folder_path)
button.pack(pady=20)

root.mainloop()
