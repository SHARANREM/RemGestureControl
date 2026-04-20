import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    """
    A standard scrollable frame for Tkinter.
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_window = ttk.Frame(canvas)

        self.scrollable_window.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_window, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class LabeledEntry(ttk.Frame):
    """
    A simple label + entry widget.
    """
    def __init__(self, container, label_text, initial_value="", **kwargs):
        super().__init__(container, **kwargs)
        self.label = ttk.Label(self, text=label_text)
        self.label.pack(side="left", padx=5)
        self.entry = ttk.Entry(self)
        self.entry.insert(0, str(initial_value))
        self.entry.pack(side="left", fill="x", expand=True, padx=5)

    def get(self):
        return self.entry.get()
