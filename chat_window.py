# chat_window.py
# --- (U3.2) - Chat UI + lmargin FIX + LAYOUT FIX ---

import tkinter as tk
from tkinter import ttk, messagebox
import database
from ui_style import *

# ===================================================================
# CHAT WINDOW
# ===================================================================

def open_chat_window(parent_root, booking_id, current_user_id, current_user_type, recipient_name):
    
    win = tk.Toplevel(parent_root)
    win.title(f"Chat with {recipient_name} (Booking #{booking_id})")
    win.geometry("500x600")
    win.configure(bg=WHITE)
    win.resizable(False, False)
    win.transient(parent_root)
    win.grab_set()

    # --- Header ---
    title = title_label(win, f"Chat: {recipient_name}")
    title.pack(side="top", pady=(15, 5)) # <-- LAYOUT FIX
    subtitle = subtitle_label(win, f"Booking ID: {booking_id}")
    subtitle.pack(side="top") # <-- LAYOUT FIX

    # --- Message Input Frame (Packed at BOTTOM first) ---
    input_frame = tk.Frame(win, bg=WHITE)
    # --- LAYOUT FIX: Pack to bottom ---
    input_frame.pack(side="bottom", fill="x", padx=15, pady=10) 

    msg_entry = styled_entry(input_frame, width=45)
    msg_entry.pack(side="left", fill="x", expand=True, ipady=8)

    def send_new_message():
        msg = msg_entry.get().strip()
        if not msg:
            return
            
        ok, err = database.send_message(booking_id, current_user_id, current_user_type, msg)
        
        if ok:
            msg_entry.delete(0, tk.END)
            load_messages() # Refresh chat
        else:
            messagebox.showerror("Error", f"Could not send message: {err}", parent=win)

    send_btn = styled_button(input_frame, "Send", command=send_new_message, width=10)
    send_btn.pack(side="right", padx=(10, 0))

    # --- Chat History Frame (Fills the remaining middle space) ---
    history_frame = tk.Frame(win, bg=SECONDARY)
    # --- LAYOUT FIX: Pack last to fill space ---
    history_frame.pack(side="top", fill="both", expand=True, padx=15, pady=10) 

    chat_history = tk.Text(history_frame, bg=SECONDARY, state="disabled", wrap="word",
                           font=NORMAL_FONT, relief="flat", bd=0, padx=10, pady=10)
    
    # Configure tags for chat bubble appearance
    chat_history.tag_configure("user_msg", justify="right", foreground=WHITE, background=PRIMARY, 
                               spacing1=5, spacing3=5, rmargin=10, 
                               lmargin1=60, lmargin2=60, 
                               font=NORMAL_FONT, relief="raised", borderwidth=1)
    
    chat_history.tag_configure("other_msg", justify="left", foreground=TEXT_DARK, background="#E8EAED", 
                               spacing1=5, spacing3=5, rmargin=60, 
                               lmargin1=10, lmargin2=10,
                               font=NORMAL_FONT, relief="raised", borderwidth=1)

    chat_history.tag_configure("timestamp", font=("Segoe UI", 8), foreground=TEXT_LIGHT, 
                               justify="right", spacing1=0, spacing3=5, rmargin=10)
    
    chat_history.tag_configure("timestamp_other", font=("Segoe UI", 8), foreground=TEXT_LIGHT, 
                               justify="left", spacing1=0, spacing3=5, 
                               lmargin1=10, lmargin2=10)

    scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=chat_history.yview)
    chat_history.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    chat_history.pack(side="left", fill="both", expand=True)

    # --- Load Messages ---
    def load_messages():
        chat_history.config(state="normal")
        chat_history.delete("1.0", tk.END)
        
        messages = database.get_messages(booking_id)
        
        for (sender_id, sender_type, message, timestamp) in messages:
            if sender_type == current_user_type:
                chat_history.insert(tk.END, f"{message}\n", "user_msg")
                chat_history.insert(tk.END, f"{timestamp}\n\n", "timestamp")
            else:
                chat_history.insert(tk.END, f"{message}\n", "other_msg")
                chat_history.insert(tk.END, f"{timestamp}\n\n", "timestamp_other")
        
        chat_history.config(state="disabled")
        chat_history.see(tk.END) # Auto-scroll to bottom

    # --- Auto-Refresh ---
    def auto_refresh_chat():
        if not win.winfo_exists():
            return
        load_messages()
        win.task_id = win.after(5000, auto_refresh_chat) # Refresh every 5 seconds

    load_messages() # Initial load
    auto_refresh_chat() # Start auto-refresh

    def on_close():
        if hasattr(win, 'task_id'):
            win.after_cancel(win.task_id)
        win.destroy()
    
    win.protocol("WM_DELETE_WINDOW", on_close)