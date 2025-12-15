# worker_dashboard.py
# --- FULLY UPGRADED (U3 - CHAT BUTTON ADDED) ---

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import database
import os
import shutil
import datetime
from ui_style import *
from chat_window import open_chat_window # <-- U3 IMPORT

# Ensure DB exists
database.connect_db()

# ===================================================================
# MAIN WORKER DASHBOARD WINDOW
# ===================================================================
def open_worker_dashboard(worker_id, worker_name):
    
    root = tk.Tk()
    root.title(f"Worker Dashboard - {worker_name}")
    root.geometry("1000x700") # Wider for chat button
    root.configure(bg=WHITE)

    # Center window
    root.update_idletasks()
    w = 1000 # Wider
    h = 700
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    # --- Header ---
    title = title_label(root, f"Welcome, {worker_name}")
    title.pack(pady=(20, 5))
    subtitle = subtitle_label(root, "Your Incoming Service Requests")
    subtitle.pack()

    # --- Top Controls ---
    top_frame = tk.Frame(root, bg=WHITE)
    top_frame.pack(pady=10)

    profile_btn = styled_button(top_frame, "My Profile", command=lambda: open_profile_edit(worker_id, root), width=15)
    profile_btn.pack(side="left", padx=10)
    
    refresh_btn = styled_button(top_frame, "Refresh Requests", command=lambda: populate_requests(), width=20)
    refresh_btn.pack(side="left", padx=10)

    # --- Requests Table Frame ---
    table_frame = tk.Frame(root, bg=WHITE)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # --- U3 UPDATE: Add customer_id to cols (but hide it) ---
    cols = ("ID", "Customer", "Phone", "Date", "Status", "Address", "Notes")
    tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=18)
    
    for c in cols:
        tree.heading(c, text=c)
        if c == "ID":
            tree.column(c, width=40, anchor="center")
        else:
            tree.column(c, width=120, anchor="w")
    
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)


    def populate_requests():
        for item in tree.get_children():
            tree.delete(item)
        data = database.get_bookings_by_worker(worker_id)
        for row in data:
            # row = (booking_id, customer_id, c.name, c.phone, b.service_date, b.status, b.address, b.notes)
            # We store customer_id and customer_name in tags
            tree.insert("", "end", values=(row[0], row[2], row[3], row[4], row[5], row[6], row[7]), tags=(row[1], row[2]))

        return data

    # --- Action Buttons ---
    action_frame = tk.Frame(root, bg=WHITE)
    action_frame.pack(pady=10)

    def accept_selected():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a booking to accept.", parent=root)
            return
        
        item = tree.item(selected)
        booking_id = item["values"][0]
        current_status = item["values"][4]

        if current_status == "Accepted":
            messagebox.showinfo("Info", "This booking is already accepted.", parent=root)
            return
        
        ok, err = database.update_booking_status(booking_id, "Accepted")
        if ok:
            messagebox.showinfo("Success", "Booking Accepted!", parent=root)
            populate_requests()
        else:
            messagebox.showerror("Error", f"Failed to accept: {err}", parent=root)

    accept_btn = styled_button(action_frame, "Accept Selected", command=accept_selected, width=18)
    accept_btn.grid(row=0, column=0, padx=10)

    def reject_selected():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a booking to reject.", parent=root)
            return
        
        booking_id = tree.item(selected)["values"][0]
        ok, err = database.update_booking_status(booking_id, "Rejected")
        if ok:
            messagebox.showinfo("Success", "Booking Rejected.", parent=root)
            populate_requests()
        else:
            messagebox.showerror("Error", f"Failed to reject: {err}", parent=root)

    reject_btn = styled_button(action_frame, "Reject Selected", command=reject_selected, width=18)
    reject_btn.grid(row=0, column=1, padx=10)
    
    def complete_selected():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a booking to mark as complete.", parent=root)
            return
            
        item = tree.item(selected)
        booking_id = item["values"][0]
        current_status = item["values"][4]
        
        if current_status != "Accepted":
            messagebox.showwarning("Info", "Only 'Accepted' bookings can be marked as complete.", parent=root)
            return

        ok, err = database.update_booking_status(booking_id, "Completed")
        if ok:
            messagebox.showinfo("Success", "Booking marked as Completed!", parent=root)
            populate_requests()
        else:
            messagebox.showerror("Error", f"Failed: {err}", parent=root)
            
    complete_btn = styled_button(action_frame, "Mark as Completed", command=complete_selected, width=20)
    complete_btn.grid(row=0, column=2, padx=10)

    # --- U3 NEW: "Open Chat" Button ---
    def open_chat_for_selected():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a booking from the list to open chat.", parent=root)
            return
        
        item = tree.item(selected)
        booking_id = item["values"][0]
        customer_id = item["tags"][0]
        customer_name = item["tags"][1]
        
        # Open the chat window
        open_chat_window(root, booking_id, worker_id, 'worker', customer_name)

    chat_btn = styled_button(action_frame, "Open Chat", command=open_chat_for_selected, width=15)
    chat_btn.grid(row=0, column=3, padx=10)
    # --- End U3 ---


    # --- Notification System (Auto-Refresh) ---
    last_count = len(populate_requests())

    def check_new_bookings():
        if not root.winfo_exists(): 
            return
            
        nonlocal last_count
        try:
            current_bookings = database.get_bookings_by_worker(worker_id)
            current_count = len(current_bookings)
            
            if current_count > last_count:
                messagebox.showinfo("New Booking", "You have a new booking request!", parent=root)
                populate_requests() 
            
            last_count = current_count
            root.task_id = root.after(5000, check_new_bookings) 
        except Exception as e:
            print(f"Error checking bookings: {e}")
            
    check_new_bookings() 

    def on_close():
        if hasattr(root, 'task_id'): 
            root.after_cancel(root.task_id)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)


    # --- Profile Edit Popup ---
    def open_profile_edit(worker_id, parent_root): 
        row = database.get_worker_profile(worker_id)
        if not row:
            messagebox.showerror("Error", "Could not load worker profile.")
            return

        win = tk.Toplevel(parent_root) 
        win.title("Edit My Profile")
        win.geometry("500x720") 
        win.configure(bg=WHITE)
        win.resizable(False, False)
        win.transient(parent_root)
        win.grab_set()

        title = title_label(win, "Edit My Profile")
        title.pack(pady=(20, 10))
        
        save_btn = styled_button(win, "Save Changes", command=lambda: save_profile(win, entries, photo_path_var, worker_id, row[9]), width=20)
        save_btn.pack(side="bottom", pady=20)

        form_canvas = tk.Canvas(win, bg=WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=form_canvas.yview)
        form_frame = tk.Frame(form_canvas, bg=WHITE)
        form_frame.bind("<Configure>", lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all")))
        form_canvas.create_window((0, 0), window=form_frame, anchor="nw")
        form_canvas.configure(yscrollcommand=scrollbar.set)
        
        form_canvas.pack(side="left", fill="both", expand=True, padx=30, pady=(0, 10))
        scrollbar.pack(side="right", fill="y")

        fields_info = {
            "Name": row[1], "Phone": row[3], "Skill": row[4],
            "Experience (Years)": row[5], "Price per Hour (₹)": row[6],
            "Availability": row[7], "Address": row[8]
        }
        
        entries = {}
        row_num = 0
        for label, value in fields_info.items():
            tk.Label(form_frame, text=f"{label}:", font=BOLD_FONT, bg=WHITE).grid(row=row_num, column=0, sticky="w", pady=(5,0))
            e = styled_entry(form_frame, width=45)
            e.insert(0, value if value is not None else "")
            e.grid(row=row_num + 1, column=0, pady=(0,10), columnspan=2)
            entries[label] = e
            row_num += 2

        photo_path_var = tk.StringVar(value=row[9] or "No photo selected.")
        
        def change_photo():
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

        upload_btn = styled_button(form_frame, "Change Photo", command=change_photo, width=15)
        upload_btn.grid(row=row_num, column=0, pady=(10,0), sticky="w")
        photo_status_label = tk.Label(form_frame, text=os.path.basename(photo_path_var.get()), font=NORMAL_FONT, bg=WHITE, fg=TEXT_LIGHT, wraplength=250, justify="left")
        photo_status_label.grid(row=row_num, column=1, pady=(10,0), sticky="w", padx=10)
        row_num += 1

        def save_profile(win, entries, photo_path_var, worker_id, old_photo_path):
            try:
                exp = int(entries["Experience (Years)"].get().strip() or 0)
                price = float(entries["Price per Hour (₹)"].get().strip() or 0.0)
            except ValueError:
                messagebox.showwarning("Input Error", "Experience and Price must be valid numbers.", parent=win)
                return
                
            new_photo = photo_path_var.get()
            if new_photo == "No photo selected.":
                new_photo = old_photo_path 

            ok, err = database.update_worker_profile(
                worker_id=worker_id,
                name=entries["Name"].get().strip(),
                phone=entries["Phone"].get().strip(),
                skill=entries["Skill"].get().strip(),
                experience=exp,
                price_per_hour=price,
                availability=entries["Availability"].get().strip(),
                address=entries["Address"].get().strip(),
                photo=new_photo
            )
            
            if ok:
                messagebox.showinfo("Success", "Profile updated successfully!", parent=win)
                win.destroy()
            else:
                messagebox.showerror("Error", f"Failed to update: {err}", parent=win)
        
    root.mainloop()