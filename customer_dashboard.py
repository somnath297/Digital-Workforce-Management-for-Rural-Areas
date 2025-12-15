# customer_dashboard.py
# --- FULLY UPGRADED (U3 - CHAT BUTTON ADDED) ---

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import database
import os
import datetime
from ui_style import *
from chat_window import open_chat_window # <-- U3 IMPORT

# Ensure DB exists (runs once on import)
database.connect_db()

# ===================================================================
# MAIN CUSTOMER DASHBOARD WINDOW
# ===================================================================
def open_customer_dashboard(user_id, user_name):
    
    customer_details = database.get_customer_details(user_id)
    if not customer_details:
        messagebox.showerror("Fatal Error", "Could not load customer profile. Logging out.")
        return

    root = tk.Tk()
    root.title(f"Customer Dashboard - {user_name}")
    root.geometry("1100x750")
    root.configure(bg=WHITE)

    # Center window
    root.update_idletasks()
    w = 1100
    h = 750
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    # --- Header ---
    title = title_label(root, f"Welcome, {user_name}")
    title.pack(pady=(20, 5))
    subtitle = subtitle_label(root, "Find & Hire Skilled Workers Near You")
    subtitle.pack()

    # --- Search & Filters Frame (Modern) ---
    top_frame = tk.Frame(root, bg=SECONDARY, height=100)
    top_frame.pack(fill="x", pady=20, padx=20)

    tk.Label(top_frame, text="Search:", bg=SECONDARY, font=BOLD_FONT).grid(row=0, column=0, padx=(10,5), pady=20)
    search_entry = styled_entry(top_frame, width=25)
    search_entry.grid(row=0, column=1, padx=5)

    tk.Label(top_frame, text="Skill:", bg=SECONDARY, font=BOLD_FONT).grid(row=0, column=2, padx=(15,5))
    skill_var = tk.StringVar(value="All")
    skill_dd = ttk.Combobox(top_frame, textvariable=skill_var, width=18, font=NORMAL_FONT, state="readonly")
    skill_dd["values"] = ["All", "Carpenter", "Plumber", "Electrician", "Painter", "Mechanic", "Cook"]
    skill_dd.current(0)
    skill_dd.grid(row=0, column=3, padx=5)

    tk.Label(top_frame, text="Availability:", bg=SECONDARY, font=BOLD_FONT).grid(row=0, column=4, padx=(15,5))
    avail_var = tk.StringVar(value="All")
    avail_dd = ttk.Combobox(top_frame, textvariable=avail_var, width=15, font=NORMAL_FONT, state="readonly")
    avail_dd["values"] = ["All", "Available", "Not Available"]
    avail_dd.current(0)
    avail_dd.grid(row=0, column=5, padx=5)

    search_btn = styled_button(top_frame, "Search", command=lambda: do_search(), width=12)
    search_btn.grid(row=0, column=6, padx=10)

    bookings_btn = styled_button(top_frame, "My Bookings", command=lambda: open_my_bookings(user_id, user_name), width=15)
    bookings_btn.grid(row=0, column=7, padx=10)
    
    def logout():
        root.destroy()
        import login 
        login.open_login_window()

    logout_btn = styled_button(top_frame, "Logout", command=logout, width=12)
    logout_btn.grid(row=0, column=8, padx=10)
    logout_btn.configure(bg="#C0392B", activebackground="#A93226") 

    # --- Worker Cards Area (Scrollable) ---
    worker_list_frame = scrollable_frame(root)
    
    image_refs = {}

    def load_image(path, size=(100, 100)):
        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading image {path}: {e}")
                return None
        return None

    def populate_cards(rows):
        for widget in worker_list_frame.winfo_children():
            widget.destroy()

        if not rows:
            tk.Label(worker_list_frame, text="No workers found matching your criteria.", font=SUBTITLE_FONT, bg=WHITE, fg=TEXT_LIGHT).pack(pady=50)
            return

        for idx, row in enumerate(rows):
            wid, name, skill, price, avail, photo_path, rating, address = row
            
            card = tk.Frame(worker_list_frame, bg=WHITE, highlightbackground=CARD_SHADOW, highlightthickness=1)
            card.pack(fill="x", padx=20, pady=8)

            img = load_image(photo_path)
            image_refs[wid] = img
            
            photo_lbl = tk.Label(card, image=img, bg=WHITE, width=100, height=100)
            if img is None:
                photo_lbl.config(text="No Pic", font=NORMAL_FONT, fg=TEXT_LIGHT, relief="solid", bd=1, width=12, height=6)
            photo_lbl.grid(row=0, column=0, rowspan=4, padx=15, pady=15)

            tk.Label(card, text=name, font=SUBTITLE_FONT, bg=WHITE, fg=TEXT_DARK).grid(row=0, column=1, sticky="w", pady=(10,0))
            tk.Label(card, text=f"Skill: {skill}", font=NORMAL_FONT, bg=WHITE, fg=TEXT_LIGHT).grid(row=1, column=1, sticky="w")
            tk.Label(card, text=f"Address: {address}", font=NORMAL_FONT, bg=WHITE, fg=TEXT_LIGHT).grid(row=2, column=1, sticky="w")
            
            price_rating_frame = tk.Frame(card, bg=WHITE)
            price_rating_frame.grid(row=3, column=1, sticky="w", pady=(0,10))
            
            tk.Label(price_rating_frame, text=f"₹{price}/hr", font=BOLD_FONT, bg=WHITE, fg=PRIMARY).pack(side="left")
            tk.Label(price_rating_frame, text=f"• ⭐ {rating:.1f} Rating", font=BOLD_FONT, bg=WHITE, fg="#FBBC04").pack(side="left", padx=10)

            btn_frame = tk.Frame(card, bg=WHITE)
            btn_frame.grid(row=0, column=2, rowspan=4, padx=20)
            
            hire_btn = styled_button(btn_frame, "Hire Now", 
                                     command=make_hire_now(wid, user_id, customer_details["address"]), 
                                     width=12)
            hire_btn.pack(pady=5)
            
            profile_btn = styled_button(btn_frame, "View Profile", command=make_view_profile(wid), width=12)
            profile_btn.pack(pady=5)
            
    def do_search():
        kw = search_entry.get().strip()
        skill = skill_var.get()
        avail = avail_var.get()
        
        results = database.search_workers(keyword=kw, skill=skill, availability=avail)
        populate_cards(results)

    def make_view_profile(worker_id):
        def view():
            row = database.get_worker_profile(worker_id)
            if not row:
                messagebox.showerror("Error", "Worker data not found.")
                return

            pf = tk.Toplevel(root)
            pf.title("Worker Profile")
            pf.geometry("450x550")
            pf.configure(bg=WHITE)
            pf.transient(root)
            pf.grab_set()
            
            img = load_image(row[9], size=(150, 150)) # row[9] is photo
            if img:
                pf.photo = img
                tk.Label(pf, image=img, bg=WHITE).pack(pady=15)
            
            title_label(pf, row[1]).pack() 
            
            details = f"""
Skill: {row[4]}
Experience: {row[5]} years
Price: ₹{row[6]}/hr
Availability: {row[7]}
Rating: ⭐ {row[10]:.1f} 

Phone: {row[3]}
Email: {row[2]}
Address: {row[8]}
"""
            tk.Label(pf, text=details, font=NORMAL_FONT, bg=WHITE, justify="left").pack(pady=10)
            
            close_btn = styled_button(pf, "Close", command=pf.destroy, width=10)
            close_btn.pack(pady=10)
        return view

    def make_hire_now(worker_id, customer_id, customer_address): 
        def hire():
            bpop = tk.Toplevel(root)
            bpop.title("Book Worker")
            bpop.geometry("450x450")
            bpop.configure(bg=WHITE)
            bpop.transient(root) 
            bpop.grab_set()

            title_label(bpop, "Confirm Booking").pack(pady=15)

            tk.Label(bpop, text="Service Date (YYYY-MM-DD HH:MM):", font=BOLD_FONT, bg=WHITE).pack(pady=(10,0))
            date_e = styled_entry(bpop, width=35)
            date_e.insert(0, (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-m-%d 10:00"))
            date_e.pack()

            tk.Label(bpop, text="Service Address:", font=BOLD_FONT, bg=WHITE).pack(pady=(10,0))
            addr_e = styled_entry(bpop, width=35)
            addr_e.insert(0, customer_address or "")
            addr_e.pack()

            tk.Label(bpop, text="Notes (e.g., 'need faucet fixed'):", font=BOLD_FONT, bg=WHITE).pack(pady=(10,0))
            notes_e = tk.Text(bpop, width=42, height=5, font=NORMAL_FONT, relief="solid", bd=1, highlightthickness=1, highlightcolor=CARD_SHADOW)
            notes_e.pack()

            def confirm_booking():
                s_date = date_e.get().strip()
                s_addr = addr_e.get().strip()
                s_notes = notes_e.get("1.0", tk.END).strip()

                if not s_date or not s_addr:
                    messagebox.showwarning("Input Error", "Date and Address are required.", parent=bpop)
                    return
                
                ok, res_id = database.create_booking(customer_id, worker_id, s_date, s_addr, s_notes)
                if ok:
                    messagebox.showinfo("Success", f"Booking Requested! (ID: {res_id})\nThe worker has been notified.", parent=bpop)
                    bpop.destroy()
                    populate_cards(database.get_worker_list_for_search()) 
                else:
                    messagebox.showerror("Error", f"Booking failed: {res_id}", parent=bpop)
            
            confirm_btn = styled_button(bpop, "Confirm Booking", command=confirm_booking, width=20)
            confirm_btn.pack(pady=20)
        return hire

    # --- Helper: My Bookings Popup ---
    def open_my_bookings(customer_id, customer_name_for_chat): # <-- U3 UPDATE
        mb = tk.Toplevel(root)
        mb.title("My Bookings")
        mb.geometry("1100x600") # Wider for new buttons
        mb.configure(bg=WHITE)
        mb.transient(root)
        mb.grab_set()

        title_label(mb, "My Booking History").pack(pady=15)
        
        cols = ("ID", "Worker", "Skill", "Date", "Status", "Address", "Action")
        tree = ttk.Treeview(mb, columns=cols, show="headings", height=15)
        for c in cols:
            tree.heading(c, text=c)
            if c == "Action":
                tree.column(c, width=120, anchor="center")
            elif c == "ID":
                tree.column(c, width=40, anchor="center")
            else:
                tree.column(c, width=120, anchor="w")
        tree.pack(fill="both", expand=True, padx=20, pady=10)

        def refresh_bookings():
            for item in tree.get_children():
                tree.delete(item)
            
            data = database.get_bookings_by_customer(customer_id)
            for row in data:
                booking_id = row[0]
                status = row[5]
                
                reviewed = database.check_if_reviewed(booking_id)
                
                action_text = ""
                if status == "Completed" and not reviewed:
                    action_text = "Leave Review"
                elif reviewed:
                    action_text = "Reviewed"
                
                # Store (booking_id, worker_id, worker_name, skill, ... , action)
                tree.insert("", "end", values=(row[0], row[2], row[3], row[4], row[5], row[6], action_text), tags=(row[1], row[2])) # Store worker_id, worker_name in tags

        def open_review_popup(booking_id, worker_id):
            r_pop = tk.Toplevel(mb)
            r_pop.title("Leave a Review")
            r_pop.geometry("400x450")
            r_pop.configure(bg=WHITE)
            r_pop.transient(mb)
            r_pop.grab_set()
            
            title_label(r_pop, "Rate this Service").pack(pady=15)
            
            tk.Label(r_pop, text="Rating (1-5):", font=BOLD_FONT, bg=WHITE).pack(pady=(10,0))
            rating_var = tk.IntVar(value=5)
            rating_scale = tk.Scale(r_pop, from_=1, to=5, orient="horizontal", variable=rating_var,
                                    bg=WHITE, troughcolor=SECONDARY, activebackground=PRIMARY,
                                    highlightthickness=0, length=200)
            rating_scale.pack()
            
            tk.Label(r_pop, text="Review:", font=BOLD_FONT, bg=WHITE).pack(pady=(10,0))
            review_text = tk.Text(r_pop, width=40, height=8, font=NORMAL_FONT, relief="solid", bd=1, highlightthickness=1, highlightcolor=CARD_SHADOW)
            review_text.pack()
            
            def submit_review():
                rating = rating_var.get()
                review = review_text.get("1.0", tk.END).strip()
                
                if not review:
                    messagebox.showwarning("Input Error", "Please write a short review.", parent=r_pop)
                    return
                
                ok, err = database.add_review(booking_id, customer_id, worker_id, rating, review)
                
                if ok:
                    messagebox.showinfo("Success", "Thank you for your review!", parent=r_pop)
                    r_pop.destroy()
                    refresh_bookings() 
                    populate_cards(database.get_worker_list_for_search()) 
                else:
                    messagebox.showerror("Error", f"Failed to submit: {err}", parent=r_pop)
            
            submit_btn = styled_button(r_pop, "Submit Review", command=submit_review, width=20)
            submit_btn.pack(pady=20)

        def on_tree_click(event):
            item_id = tree.identify_row(event.y)
            if not item_id:
                return
            
            column = tree.identify_column(event.x)
            if column == "#7": # Action column
                item = tree.item(item_id)
                action = item["values"][6]
                
                if action == "Leave Review":
                    booking_id = item["values"][0]
                    worker_id = item["tags"][0] 
                    open_review_popup(booking_id, worker_id)

        tree.bind("<Button-1>", on_tree_click)

        # --- U3 NEW: "Open Chat" Button ---
        def open_chat_for_selected():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a booking from the list to open chat.", parent=mb)
                return
            
            item = tree.item(selected)
            booking_id = item["values"][0]
            worker_id = item["tags"][0]
            worker_name = item["tags"][1]
            
            # Open the chat window
            open_chat_window(mb, booking_id, customer_id, 'customer', worker_name)

        chat_btn = styled_button(mb, "Open Chat for Selected Booking", command=open_chat_for_selected, width=30)
        chat_btn.pack(side="left", padx=20, pady=(0, 15))
        # --- End U3 ---

        last_status_map = {}
        def refresh_and_get_map():
            bookings_data = database.get_bookings_by_customer(customer_id)
            new_map = {}
            
            # Clear tree first
            for item in tree.get_children():
                tree.delete(item)
            
            # Repopulate tree and build map
            for row in bookings_data:
                booking_id = row[0]
                status = row[5]
                new_map[booking_id] = status
                
                reviewed = database.check_if_reviewed(booking_id)
                action_text = "Reviewed" if reviewed else ("Leave Review" if status == "Completed" else "")
                
                tree.insert("", "end", values=(row[0], row[2], row[3], row[4], row[5], row[6], action_text), tags=(row[1], row[2]))
            
            return new_map

        last_status_map = refresh_and_get_map()

        def check_customer_notifications():
            nonlocal last_status_map 
            if not mb.winfo_exists(): 
                return
            
            new_map = refresh_and_get_map()
            
            for bid, status in new_map.items():
                old_status = last_status_map.get(bid)
                if old_status and old_status != status:
                    if status == "Accepted":
                        messagebox.showinfo("Booking Update", f"Booking #{bid} has been ACCEPTED.", parent=mb)
                    elif status == "Rejected":
                        messagebox.showwarning("Booking Update", f"Booking #{bid} has been REJECTED.", parent=mb)
                    elif status == "Completed":
                        messagebox.showinfo("Booking Update", f"Booking #{bid} is now COMPLETE. Please leave a review.", parent=mb)
            
            last_status_map = new_map 
            mb.task_id = mb.after(5000, check_customer_notifications) 

        check_customer_notifications() 

        def on_close():
            if hasattr(mb, 'task_id'): 
                mb.after_cancel(mb.task_id)
            mb.destroy()
            populate_cards(database.get_worker_list_for_search()) 
        mb.protocol("WM_DELETE_WINDOW", on_close)


    # --- Initial Load ---
    populate_cards(database.get_worker_list_for_search())
    
    root.mainloop()