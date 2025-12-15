import tkinter as tk
from tkinter import ttk, messagebox
import database
from ui_style import *

# Import dashboard functions
try:
    from customer_dashboard import open_customer_dashboard
except ImportError:
    def open_customer_dashboard(user_id, user_name):
        messagebox.showerror("Error", "Customer dashboard file not found!")

try:
    from worker_dashboard import open_worker_dashboard
except ImportError:
    def open_worker_dashboard(worker_id, worker_name):
        messagebox.showerror("Error", "Worker dashboard file not found!")

# --- U4.3 ADMIN IMPORT ---
try:
    from admin_dashboard import open_admin_dashboard
except ImportError:
    def open_admin_dashboard():
        messagebox.showerror("Error", "Admin dashboard file not found!")
# --- END U4.3 ---

# Import registration functions
try:
    from register_customer import open_customer_registration
except ImportError:
    def open_customer_registration(parent_root): 
        messagebox.showerror("Error", "Customer registration file not found!")

try:
    from register_worker import open_worker_registration
except ImportError:
    def open_worker_registration(parent_root): 
        messagebox.showerror("Error", "Worker registration file not found!")


# ===================================================================
# MAIN LOGIN WINDOW
# ===================================================================
def open_login_window():
    
    database.connect_db()

    root = tk.Tk()
    root.title("Village Service App - Login")
    root.geometry("450x500") 
    root.configure(bg=WHITE)
    root.resizable(False, False)

    # --- Center Window ---
    root.update_idletasks()
    width = 450
    height = 500
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # --- Title ---
    title = title_label(root, "Village Service App")
    title.pack(pady=(30, 10))

    subtitle = subtitle_label(root, "Login Portal")
    subtitle.pack(pady=5)

    # --- Login Form Frame ---
    form_frame = tk.Frame(root, bg=WHITE)
    form_frame.pack(pady=10, padx=20)

    tk.Label(form_frame, text="Login As:", font=BOLD_FONT, bg=WHITE).grid(row=0, column=0, sticky="w", pady=(10,0))
    login_type_var = tk.StringVar(value="Customer") 
    login_type_dd = ttk.Combobox(form_frame, textvariable=login_type_var, 
                                 values=["Customer", "Worker", "Admin"], 
                                 font=NORMAL_FONT, width=38, state="readonly")
    login_type_dd.grid(row=1, column=0, pady=(0,10))

    tk.Label(form_frame, text="Email or Username:", font=BOLD_FONT, bg=WHITE).grid(row=2, column=0, sticky="w", pady=(5,0))
    email_entry = styled_entry(form_frame, width=40)
    email_entry.grid(row=3, column=0, pady=(0,10))
    email_entry.insert(0, "admin") # Default text for easy testing

    tk.Label(form_frame, text="Password:", font=BOLD_FONT, bg=WHITE).grid(row=4, column=0, sticky="w", pady=(5,0))
    pass_entry = styled_entry(form_frame, width=40)
    pass_entry.config(show="*")
    pass_entry.grid(row=5, column=0, pady=(0,15))
    pass_entry.insert(0, "admin123") # Default text for easy testing

    # --- Verify Login Function ---
    def verify_login():
        user_type = login_type_var.get()
        login_id = email_entry.get().strip()
        password = pass_entry.get().strip()

        if not login_id or not password:
            messagebox.showwarning("Input Error", "Please fill all fields.", parent=root)
            return

        # --- CUSTOMER LOGIN ---
        if user_type == "Customer":
            ok, user_data = database.verify_customer(login_id, password)
            if ok:
                root.destroy()
                open_customer_dashboard(user_data["user_id"], user_data["name"])
            else:
                messagebox.showerror("Login Failed", "Invalid customer credentials!", parent=root)

        # --- WORKER LOGIN ---
        elif user_type == "Worker":
            ok, worker_data = database.verify_worker(login_id, password)
            if ok:
                root.destroy()
                open_worker_dashboard(worker_data["worker_id"], worker_data["name"])
            else:
                messagebox.showerror("Login Failed", "Invalid worker credentials!", parent=root)
        
        # --- ADMIN LOGIN (U4.3 UPDATE) ---
        elif user_type == "Admin":
            conn = database.get_connection()
            cursor = conn.cursor()
            hashed_pw = database.hash_password(password) 
            
            cursor.execute("SELECT * FROM admin WHERE username=? AND password=?", (login_id, hashed_pw))
            row = cursor.fetchone()
            conn.close()

            if row:
                # --- UPDATE ---
                root.destroy()
                open_admin_dashboard() # Open the admin dashboard
                # --- END UPDATE ---
            else:
                messagebox.showerror("Login Failed", "Invalid admin credentials!", parent=root)

    # --- Login Button ---
    login_btn = styled_button(form_frame, "Login", command=verify_login, width=35)
    login_btn.grid(row=6, column=0, pady=10)

    # --- Registration Buttons ---
    tk.Label(root, text="Don't have an account?", font=NORMAL_FONT, bg=WHITE).pack(pady=(15, 5))
    
    reg_frame = tk.Frame(root, bg=WHITE)
    reg_frame.pack()
    
    reg_cust_btn = styled_button(reg_frame, "Register as Customer", command=lambda: open_customer_registration(root), width=20)
    reg_cust_btn.grid(row=0, column=0, padx=5)
    
    reg_work_btn = styled_button(reg_frame, "Register as Worker", command=lambda: open_worker_registration(root), width=20)
    reg_work_btn.grid(row=0, column=1, padx=5)


    root.mainloop()

# ===================================================================
# RUN THE APP
# ===================================================================
if __name__ == "__main__":
    open_login_window()