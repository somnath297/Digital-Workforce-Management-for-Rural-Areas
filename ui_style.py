# ui_style.py
# Modern UI theme for Village Service App (Tkinter)
# --- UPDATED with **kwargs in styled_entry ---

import tkinter as tk
from tkinter import ttk

# -----------------------------
# COLOR PALETTE
# -----------------------------
PRIMARY = "#1A73E8"       # Google Blue
SECONDARY = "#F1F3F4"     # Light Grey
WHITE = "#FFFFFF"
TEXT_DARK = "#202124"
TEXT_LIGHT = "#5F6368"
CARD_BG = "#FFFFFF"
CARD_SHADOW = "#DADCE0"

# -----------------------------
# GLOBAL FONT STYLE
# -----------------------------
TITLE_FONT = ("Segoe UI", 20, "bold")
SUBTITLE_FONT = ("Segoe UI", 12, "bold")
NORMAL_FONT = ("Segoe UI", 11)
BOLD_FONT = ("Segoe UI", 11, "bold")

# -----------------------------
# APPLY MODERN BUTTON STYLE
# -----------------------------
def styled_button(parent, text, command=None, width=15):
    btn = tk.Button(parent,
                    text=text,
                    command=command,
                    bg=PRIMARY,
                    fg=WHITE,
                    font=("Segoe UI", 11, "bold"),
                    relief="flat",
                    activebackground="#1557B0",
                    activeforeground=WHITE,
                    bd=0,
                    padx=10, pady=5)
    btn.configure(width=width)
    return btn

# -----------------------------
# MODERN ENTRY STYLE (FIXED)
# -----------------------------
def styled_entry(parent, width=30, **kwargs): # <-- Added **kwargs
    """Creates a styled Entry widget, accepting extra arguments."""
    entry = tk.Entry(parent,
                     font=("Segoe UI", 11),
                     bg=WHITE,
                     fg=TEXT_DARK,
                     relief="solid",
                     bd=1,
                     width=width,    # <-- Moved width here
                     **kwargs)       # <-- Pass extra args (like show="*")
    return entry

# -----------------------------
# MODERN LABEL (TITLE)
# -----------------------------
def title_label(parent, text):
    return tk.Label(parent,
                    text=text,
                    font=TITLE_FONT,
                    fg=PRIMARY,
                    bg=WHITE)

# -----------------------------
# SUBTITLE LABEL
# -----------------------------
def subtitle_label(parent, text):
    return tk.Label(parent,
                    text=text,
                    font=SUBTITLE_FONT,
                    fg=TEXT_DARK,
                    bg=WHITE)

# -----------------------------
# CARD FRAME (ROUNDED LOOK)
# -----------------------------
def card_frame(parent, pad=10):
    frame = tk.Frame(parent,
                     bg=CARD_BG,
                     highlightbackground=CARD_SHADOW,
                     highlightthickness=2,
                     bd=0)
    frame.pack(padx=pad, pady=pad)
    return frame

# -----------------------------
# WORKER CARD GENERATOR
# -----------------------------
def create_worker_card(parent, name, skill, price, rating, command_hire):
    frame = tk.Frame(parent, bg="white", highlightbackground="#DADCE0",
                     highlightthickness=1, padx=15, pady=10)

    # Name
    name_lbl = tk.Label(frame, text=name, font=("Segoe UI", 12, "bold"),
                        fg=TEXT_DARK, bg="white")
    name_lbl.grid(row=0, column=0, sticky="w")

    # Skill
    skill_lbl = tk.Label(frame, text=f"Skill: {skill}",
                         font=("Segoe UI", 10), bg="white", fg=TEXT_LIGHT)
    skill_lbl.grid(row=1, column=0, sticky="w")

    # Price
    price_lbl = tk.Label(frame, text=f"Price: ₹{price}/hr",
                         font=("Segoe UI", 10), bg="white", fg=TEXT_LIGHT)
    price_lbl.grid(row=2, column=0, sticky="w")

    # Rating
    rating_lbl = tk.Label(frame, text=f"⭐ {rating:.1f}", # Added formatting
                          font=("Segoe UI", 10, "bold"), fg="#FBBC04", bg="white")
    rating_lbl.grid(row=3, column=0, sticky="w")

    # Hire Button
    hire_btn = styled_button(frame, "Hire Now", command=command_hire, width=12)
    hire_btn.grid(row=0, column=1, rowspan=4, padx=20)

    return frame

# -----------------------------
# COMBOBOX STYLE
# -----------------------------
def styled_combobox(parent, values):
    combo = ttk.Combobox(parent, values=values, font=("Segoe UI", 11), width=27, state="readonly")
    combo.set("Select")
    return combo

# -----------------------------
# SCROLLABLE CANVAS (for worker list)
# -----------------------------
def scrollable_frame(parent):
    canvas = tk.Canvas(parent, bg=WHITE, highlightthickness=0)
    frame = tk.Frame(canvas, bg=WHITE)

    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    frame.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    return frame