# admin_dashboard.py
# --- NEW FILE (U4.1) - Admin Dashboard UI Skeleton ---

import tkinter as tk
from tkinter import ttk, messagebox
import database
from ui_style import *

# ===================================================================
# MAIN ADMIN DASHBOARD WINDOW
# ===================================================================
def open_admin_dashboard():
    
    root = tk.Tk()
    root.title("Admin Dashboard - Village Service App")
    root.geometry("1100x700")
    root.configure(bg=WHITE)

    # Center window
    root.update_idletasks()
    w = 1100
    h = 700
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    # --- Header ---
    title = title_label(root, "Admin Dashboard")
    title.pack(pady=(20, 10))

    # --- Tabbed Interface ---
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    # Create tab frames
    stats_frame = tk.Frame(notebook, bg=WHITE)
    users_frame = tk.Frame(notebook, bg=WHITE)
    workers_frame = tk.Frame(notebook, bg=WHITE)
    bookings_frame = tk.Frame(notebook, bg=WHITE)

    notebook.add(stats_frame, text="Dashboard Stats")
    notebook.add(users_frame, text="Manage Customers")
    notebook.add(workers_frame, text="Manage Workers")
    notebook.add(bookings_frame, text="View All Bookings")

    # ==================================
    # TAB 1: DASHBOARD STATS
    # ==================================
    stats_container = tk.Frame(stats_frame, bg=WHITE)
    stats_container.pack(pady=40)
    
    total_users_var = tk.StringVar(value="Total Customers:\n--")
    total_workers_var = tk.StringVar(value="Total Workers:\n--")
    total_bookings_var = tk.StringVar(value="Total Bookings:\n--")

    # Stat Box Style
    def create_stat_box(parent, text_var):
        box = tk.Label(parent, textvariable=text_var, font=TITLE_FONT, 
                       bg=SECONDARY, fg=PRIMARY, relief="solid", bd=1,
                       width=15, height=4, padx=20, pady=20)
        box.pack(side="left", padx=20, pady=20)

    create_stat_box(stats_container, total_users_var)
    create_stat_box(stats_container, total_workers_var)
    create_stat_box(stats_container, total_bookings_var)

    def load_stats():
        # This function will be fully built in Step U4.2
        try:
            stats = database.get_app_stats() # (Pending Step U4.2)
            total_users_var.set(f"Total Customers:\n{stats['users']}")
            total_workers_var.set(f"Total Workers:\n{stats['workers']}")
            total_bookings_var.set(f"Total Bookings:\n{stats['bookings']}")
        except Exception as e:
            print(f"Stats error (normal if DB not updated): {e}")

    refresh_stats_btn = styled_button(stats_frame, "Refresh Stats", command=load_stats, width=20)
    refresh_stats_btn.pack(pady=20)

    # ==================================
    # TAB 2: MANAGE CUSTOMERS
    # ==================================
    users_table_frame = tk.Frame(users_frame, bg=WHITE)
    users_table_frame.pack(fill="both", expand=True, pady=10)
    
    user_cols = ("ID", "Name", "Email", "Phone", "Address")
    user_tree = ttk.Treeview(users_table_frame, columns=user_cols, show="headings", height=25)
    for col in user_cols:
        user_tree.heading(col, text=col)
        user_tree.column(col, width=150)
    user_tree.pack(fill="both", expand=True, side="left")
    
    user_scroll = ttk.Scrollbar(users_table_frame, orient="vertical", command=user_tree.yview)
    user_tree.configure(yscroll=user_scroll.set)
    user_scroll.pack(side="right", fill="y")

    def load_users():
        for i in user_tree.get_children(): user_tree.delete(i)
        try:
            users = database.get_all_users() # (Pending Step U4.2)
            for user in users:
                user_tree.insert("", "end", values=user)
        except Exception as e:
            print(f"User load error (normal if DB not updated): {e}")

    user_btn_frame = tk.Frame(users_frame, bg=WHITE)
    user_btn_frame.pack(pady=10)
    
    refresh_users_btn = styled_button(user_btn_frame, "Refresh", command=load_users, width=15)
    refresh_users_btn.pack(side="left", padx=10)
    
    def delete_user():
        selected = user_tree.focus()
        if not selected:
            messagebox.showwarning("Error", "Please select a customer to delete.", parent=root)
            return
        user_id = user_tree.item(selected)["values"][0]
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete customer ID {user_id}? This is permanent.", parent=root):
            try:
                database.delete_user(user_id) # (Pending Step U4.2)
                messagebox.showinfo("Success", "Customer deleted.", parent=root)
                load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed: {e}", parent=root)

    delete_user_btn = styled_button(user_btn_frame, "Delete Selected", command=delete_user, width=15)
    delete_user_btn.pack(side="left", padx=10)
    delete_user_btn.config(bg="#C0392B", activebackground="#A93226")

    # ==================================
    # TAB 3: MANAGE WORKERS
    # ==================================
    workers_table_frame = tk.Frame(workers_frame, bg=WHITE)
    workers_table_frame.pack(fill="both", expand=True, pady=10)
    
    worker_cols = ("ID", "Name", "Skill", "Phone", "Rating", "Availability")
    worker_tree = ttk.Treeview(workers_table_frame, columns=worker_cols, show="headings", height=25)
    for col in worker_cols:
        worker_tree.heading(col, text=col)
        worker_tree.column(col, width=150)
    worker_tree.pack(fill="both", expand=True, side="left")
    
    worker_scroll = ttk.Scrollbar(workers_table_frame, orient="vertical", command=worker_tree.yview)
    worker_tree.configure(yscroll=worker_scroll.set)
    worker_scroll.pack(side="right", fill="y")

    def load_workers():
        for i in worker_tree.get_children(): worker_tree.delete(i)
        try:
            workers = database.get_all_workers() # (Pending Step U4.2)
            for w in workers:
                worker_tree.insert("", "end", values=w)
        except Exception as e:
            print(f"Worker load error (normal if DB not updated): {e}")

    worker_btn_frame = tk.Frame(workers_frame, bg=WHITE)
    worker_btn_frame.pack(pady=10)
    
    refresh_workers_btn = styled_button(worker_btn_frame, "Refresh", command=load_workers, width=15)
    refresh_workers_btn.pack(side="left", padx=10)
    
    def delete_worker():
        selected = worker_tree.focus()
        if not selected:
            messagebox.showwarning("Error", "Please select a worker to delete.", parent=root)
            return
        worker_id = worker_tree.item(selected)["values"][0]
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete worker ID {worker_id}? This is permanent.", parent=root):
            try:
                database.delete_worker(worker_id) # (Pending Step U4.2)
                messagebox.showinfo("Success", "Worker deleted.", parent=root)
                load_workers()
            except Exception as e:
                messagebox.showerror("Error", f"Delete failed: {e}", parent=root)

    delete_worker_btn = styled_button(worker_btn_frame, "Delete Selected", command=delete_worker, width=15)
    delete_worker_btn.pack(side="left", padx=10)
    delete_worker_btn.config(bg="#C0392B", activebackground="#A93226")

    # ==================================
    # TAB 4: VIEW ALL BOOKINGS
    # ==================================
    bookings_table_frame = tk.Frame(bookings_frame, bg=WHITE)
    bookings_table_frame.pack(fill="both", expand=True, pady=10)
    
    booking_cols = ("ID", "Customer ID", "Worker ID", "Date", "Status", "Address")
    booking_tree = ttk.Treeview(bookings_table_frame, columns=booking_cols, show="headings", height=25)
    for col in booking_cols:
        booking_tree.heading(col, text=col)
        booking_tree.column(col, width=150)
    booking_tree.pack(fill="both", expand=True, side="left")
    
    booking_scroll = ttk.Scrollbar(bookings_table_frame, orient="vertical", command=booking_tree.yview)
    booking_tree.configure(yscroll=booking_scroll.set)
    booking_scroll.pack(side="right", fill="y")

    def load_bookings():
        for i in booking_tree.get_children(): booking_tree.delete(i)
        try:
            bookings = database.get_all_bookings() # (Pending Step U4.2)
            for b in bookings:
                booking_tree.insert("", "end", values=b)
        except Exception as e:
            print(f"Bookings load error (normal if DB not updated): {e}")
            
    refresh_bookings_btn = styled_button(bookings_frame, "Refresh All Bookings", command=load_bookings, width=25)
    refresh_bookings_btn.pack(pady=10)

    # --- Initial Load ---
    load_stats()
    load_users()
    load_workers()
    load_bookings()

    root.mainloop()

# This is so you can test the UI layout directly if you want
if __name__ == "__main__":
    open_admin_dashboard()