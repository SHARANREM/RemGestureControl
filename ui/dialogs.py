import tkinter as tk
from tkinter import messagebox

class Dialogs:
    """
    Utility class for common dialogs.
    """
    @staticmethod
    def show_error(title: str, message: str) -> None:
        messagebox.showerror(title, message)

    @staticmethod
    def show_info(title: str, message: str) -> None:
        messagebox.showinfo(title, message)

    @staticmethod
    def ask_confirmation(title: str, message: str) -> bool:
        return messagebox.askyesno(title, message)
