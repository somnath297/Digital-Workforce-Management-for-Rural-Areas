# register_worker.py
# --- FULLY UPGRADED (U1.4) + Height Adjusted ---

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import database
from ui_style import *
import os
import shutil # For copying the file
import datetime # For unique filenames

# ===================================================================
# WORKER REGISTRATION WINDOW
# ===================================================================
def open_worker_registration(parent_root):

    # Ensure DB tables exist
    database.connect_db() 
    
    win = tk.Toplevel(parent_root)
    win.title("Worker Registration")
    # --- HEIGHT CHANGE: 700 -> 650 ---
    win.geometry("500x650") 
    win.configure(bg=WHITE)
    win.resizable(False, False)

    # Center window
    win.update_idletasks()
    w = 500
    h = 650 # --- HEIGHT CHANGE ---
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")
    
    win.transient(parent_root) # Keep on top
    win.grab_set() # Modal

    # --- Title ---
    title = title_label(win, "Create Worker Account")
    title.pack(pady=(20, 10))

    # --- Register Button (Packed at the bottom FIRST) ---
    reg_btn = styled_button(win, "Register Worker Account", command=lambda: do_register(), width=25)
    reg_btn.pack(side="bottom", pady=20)

    # --- Form Frame (Scrollable) ---
    # This canvas will fill the space ABOVE the button
    form_canvas = tk.Canvas(win, bg=WHITE, highlightthickness=0)
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=form_canvas.yview)
    form_frame = tk.Frame(form_canvas, bg=WHITE)
    
    form_frame.bind(
        "<Configure>",
        lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all"))
    )

    form_canvas.create_window((0, 0), window=form_frame, anchor="nw")
    form_canvas.configure(yscrollcommand=scrollbar.set)
    
    form_canvas.pack(side="left", fill="both", expand=True, padx=30, pady=(0, 10))
    scrollbar.pack(side="right", fill="y")

    # --- Form Fields ---
    tk.Label(form_frame, text="Full Name:", font=BOLD_FONT, bg=WHITE).grid(row=0, column=0, sticky="w", pady=(10,0))
    name_e = styled_entry(form_frame, width=45)
    name_e.grid(row=1, column=0, pady=(0,10), columnspan=2)

    tk.Label(form_frame, text="Email:", font=BOLD_FONT, bg=WHITE).grid(row=2, column=0, sticky="w", pady=(5,0))
    email_e = styled_entry(form_frame, width=45)
    email_e.grid(row=3, column=0, pady=(0,10), columnspan=2)

    tk.Label(form_frame, text="Phone Number:", font=BOLD_FONT, bg=WHITE).grid(row=4, column=0, sticky="w", pady=(5,0))
    phone_e = styled_entry(form_frame, width=45)
    phone_e.grid(row=5, column=0, pady=(0,10), columnspan=2)

    tk.Label(form_frame, text="Password:", font=BOLD_FONT, bg=WHITE).grid(row=6, column=0, sticky="w", pady=(5,0))
    pass_e = styled_entry(form_frame, width=45, show="*")
    pass_e.grid(row=7, column=0, pady=(0,10), columnspan=2)

    tk.Label(form_frame, text="Primary Skill (e.g., Plumber):", font=BOLD_FONT, bg=WHITE).grid(row=8, column=0, sticky="w", pady=(5,0))
    skill_e = styled_entry(form_frame, width=45)
    skill_e.grid(row=9, column=0, pady=(0,10), columnspan=2)

    tk.Label(form_frame, text="Experience (Years):", font=BOLD_FONT, bg=WHITE).grid(row=10, column=0, sticky="w", pady=(5,0))
    exp_e = styled_entry(form_frame, width=45)
    exp_e.grid(row=11, column=0, pady=(0,10), columnspan=2)

    tk.Label(form_frame, text="Price per Hour (₹):", font=BOLD_FONT, bg=WHITE).grid(row=12, column=0, sticky="w", pady=(5,0))
    price_e = styled_entry(form_frame, width=45)
    price_e.grid(row=13, column=0, pady=(0,10), columnspan=2)

    tk.Label(form_frame, text="Availability:", font=BOLD_FONT, bg=WHITE).grid(row=14, column=0, sticky="w", pady=(5,0))
    avail_e = styled_entry(form_frame, width=45)
    avail_e.insert(0, "Available") # Default value
    avail_e.grid(row=15, column=0, pady=(0,10), columnspan=2)

    tk.Label(form_frame, text="Address:", font=BOLD_FONT, bg=WHITE).grid(row=16, column=0, sticky="w", pady=(5,0))
    addr_e = styled_entry(form_frame, width=45)
    addr_e.grid(row=17, column=0, pady=(0,10), columnspan=2)

    # --- Photo Upload ---
    photo_path_var = tk.StringVar(value="No photo selected.")
    
    def select_photo():
        assets_dir = "assets/photos"
        os.makedirs(assets_dir, exist_ok=True)
        
        filepath = filedialog.askopenfilename(
            title="Select Profile Photo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")],
            parent=win
        )
        if not filepath:
            return

        try:
            filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(filepath)}"
            dest_path = os.path.join(assets_dir, filename)
            shutil.copy(filepath, dest_path)
            
            photo_path_var.set(dest_path) 
            photo_status_label.config(text=f"Selected: {filename}", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save photo: {e}", parent=win)
            photo_path_var.set("No photo selected.")

    upload_btn = styled_button(form_frame, "Upload Photo", command=select_photo, width=15)
    upload_btn.grid(row=18, column=0, pady=(10,0), sticky="w")
    
    photo_status_label = tk.Label(form_frame, textvariable=photo_path_var, font=NORMAL_FONT, bg=WHITE, fg=TEXT_LIGHT, wraplength=250, justify="left")
    photo_status_label.grid(row=18, column=1, pady=(10,0), sticky="w", padx=10)


    # --- Registration Function ---
    def do_register():
        name = name_e.get().strip()
        email = email_e.get().strip()
        phone = phone_e.get().strip()
        pwd = pass_e.get().strip()
        skill = skill_e.get().strip()
        exp_str = exp_e.get().strip()
        price_str = price_e.get().strip()
        avail = avail_e.get().strip()
        addr = addr_e.get().strip()
        photo = photo_path_var.get()
        
        if photo == "No photo selected.":
            photo = None

        if not name or not pwd or (not email and not phone):
            messagebox.showwarning("Input Error", "Please provide Name, Password, and either Email or Phone.", parent=win)
            return
        
        try:
            exp = int(exp_str) if exp_str else 0
            price = float(price_str) if price_str else 0.0
        except ValueError:
            messagebox.showwarning("Input Error", "Experience and Price must be valid numbers.", parent=win)
            return

        ok, err_msg = database.register_worker(
            name, email, phone, pwd, skill, exp, price, avail, addr, photo
        )
        
        if ok:
            messagebox.showinfo("Success", "Worker registration successful! You can now log in.", parent=win)
            win.destroy()
        else:
            messagebox.showerror("Error", f"Registration failed: {err_msg}", parent=win)