# register_customer.py
# --- FULLY UPGRADED WITH MODERN UI (U1.3) ---

import tkinter as tk
from tkinter import messagebox
import database
from ui_style import *

# ===================================================================
# CUSTOMER REGISTRATION WINDOW
# ===================================================================
def open_customer_registration(parent_root):
    
    # Ensure DB tables exist before trying to register
    database.connect_db() 
    
    win = tk.Toplevel()
    win.title("Customer Registration")
    win.geometry("450x550")
    win.configure(bg=WHITE)
    win.resizable(False, False)

    # Center window
    win.update_idletasks()
    w = 450
    h = 550
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")
    
    win.transient() # Keep on top
    win.grab_set() # Modal

    # --- Title ---
    title = title_label(win, "Create Customer Account")
    title.pack(pady=(20, 10))

    # --- Form Frame ---
    form_frame = tk.Frame(win, bg=WHITE)
    form_frame.pack(pady=10, padx=20)

    # --- Form Fields ---
    tk.Label(form_frame, text="Full Name:", font=BOLD_FONT, bg=WHITE).grid(row=0, column=0, sticky="w", pady=(10,0))
    name_e = styled_entry(form_frame, width=40)
    name_e.grid(row=1, column=0, pady=(0,10))

    tk.Label(form_frame, text="Email:", font=BOLD_FONT, bg=WHITE).grid(row=2, column=0, sticky="w", pady=(5,0))
    email_e = styled_entry(form_frame, width=40)
    email_e.grid(row=3, column=0, pady=(0,10))

    tk.Label(form_frame, text="Phone Number:", font=BOLD_FONT, bg=WHITE).grid(row=4, column=0, sticky="w", pady=(5,0))
    phone_e = styled_entry(form_frame, width=40)
    phone_e.grid(row=5, column=0, pady=(0,10))

    tk.Label(form_frame, text="Password:", font=BOLD_FONT, bg=WHITE).grid(row=6, column=0, sticky="w", pady=(5,0))
    pass_e = styled_entry(form_frame, width=40)
    pass_e.config(show="*")
    pass_e.grid(row=7, column=0, pady=(0,10))

    tk.Label(form_frame, text="Default Address (Optional):", font=BOLD_FONT, bg=WHITE).grid(row=8, column=0, sticky="w", pady=(5,0))
    addr_e = styled_entry(form_frame, width=40)
    addr_e.grid(row=9, column=0, pady=(0,10))

    # --- Registration Function ---
    def do_register():
        name = name_e.get().strip()
        email = email_e.get().strip()
        phone = phone_e.get().strip()
        pwd = pass_e.get().strip()
        addr = addr_e.get().strip()

        if not name or not pwd or (not email and not phone):
            messagebox.showwarning("Input Error", "Please provide Name, Password, and either Email or Phone.", parent=win)
            return
        
        # Call database function to register
        ok, err_msg = database.register_customer(name, email, phone, pwd, addr)
        
        if ok:
            messagebox.showinfo("Success", "Registration successful! You can now log in.", parent=win)
            win.destroy()
        else:
            messagebox.showerror("Error", f"Registration failed: {err_msg}", parent=win)

    # --- Register Button ---
    reg_btn = styled_button(win, "Register Account", command=do_register, width=25)
    reg_btn.pack(pady=20)