"""
bidder_socket_app.py
Bidder GUI for Auction Management System (Socket Version)
Tkinter + ttkbootstrap
Communicates with server via JSON over TCP
Simplified: Manual bids only
"""

import tkinter as tk
from tkinter import messagebox
from threading import Thread
import time
import socket
import json

import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText

# ================= CONFIG =================
HOST = "127.0.0.1"
PORT = 65432
REFRESH_INTERVAL = 2
CURRENCY_SYMBOL = "$"

# ================= WIN TRACKING =================
shown_wins = set()  # prevent repeated popups
auction_last_status = {}   # item_id -> last known status

# ================= HELPERS =================
def send_request(request):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(request).encode())
            response = s.recv(65536)
            if not response:
                return {"status": "error", "message": "No response from server"}
            return json.loads(response.decode())
    except Exception as e:
        return {"status": "error", "message": str(e)}

def show_info(title, message):
    messagebox.showinfo(title, message)

def show_error(title, message):
    messagebox.showerror(title, message)

def validate_float_entry(entry):
    try:
        float(entry.get())
        return True
    except ValueError:
        show_error("Invalid Input", "Please enter a valid number")
        return False

def add_placeholder(entry, placeholder_text):
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, "end")
            entry.config(foreground="black")
    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, placeholder_text)
            entry.config(foreground="grey")
    entry.insert(0, placeholder_text)
    entry.config(foreground="grey")
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    def on_keypress(event):
        if entry.get() == placeholder_text:
            entry.delete(0, "end")
            entry.config(foreground="black")
    entry.bind("<Key>", on_keypress)

# ================= APP INIT =================
app = tb.Window(title="Auction Management System — Bidder Panel", themename="flatly", size=(1000, 620))

# ================= HEADER =================
header = tb.Frame(app, padding=15)
header.pack(fill="x")

tb.Label(header, text="Auction Management System", font=("Segoe UI", 20, "bold")).pack(anchor="w")
bidder_label = tb.Label(header, text="Bidder Panel", font=("Segoe UI", 11), foreground="#666666")
bidder_label.pack(anchor="w")

# ================= HELP / GUIDE BUTTON =================
def show_help_guide():
    guide_window = tb.Toplevel(app)
    guide_window.title("Help / Guide")
    guide_window.geometry("600x480")
    guide_window.resizable(False, False)
    guide_window.grab_set()
    guide_window.attributes("-toolwindow", True)  # remove min/max buttons on Windows

    frame = tb.Frame(guide_window, padding=10)
    frame.pack(fill="both", expand=True)

    sections = {
        "What is this Tool?": (
            "This is a real-time Auction Management System for bidders. "
            "It allows users to view live auctions and place manual bids. "
            "It communicates with the server via JSON over TCP."
        ),
        "Key Features": (
            "- Live auction feed with auto-refresh\n"
            "- Place bids and track highest bidder\n"
            "- View auction details: start/end time, status, visibility, auto-extend\n"
            "- Bidding disabled automatically for closed auctions\n"
            "- Responsive GUI built with Tkinter + ttkbootstrap"
        ),
        "Use Case": (
            "- Bidders who want to participate in online auctions remotely\n"
            "- Ideal for real-time auction monitoring and manual bidding"
        ),
        "About Developer": (
            "- Developed by Mate Technologies (https://github.com/rogers-cyber)\n"
            "- Built with Python, Tkinter, and SQLite\n"
            "- Open-source and educational project for learning real-time networking and GUIs"
        )
    }

    for title, text in sections.items():
        tb.Label(frame, text=title, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 0))
        tb.Label(frame, text=text, font=("Segoe UI", 10), wraplength=560, justify="left").pack(anchor="w", pady=(2, 5))

    tb.Button(frame, text="Close", bootstyle="secondary", width=15,
              command=guide_window.destroy).pack(pady=10)

# ================= BIDDER LOGIN =================
login_frame = tb.Labelframe(app, text="Login / Register", padding=15)
login_frame.pack(fill="x", padx=15, pady=10)

# Info / Description for Bidder ID
info_text = (
    "Bidder ID is your unique identifier used to place bids in auctions. "
    "You can create your own ID to manage your bids. "
    "Using a different Bidder ID is like opening another account. "
    "If you want to continue managing your current bids, use your existing ID."
)
tb.Label(login_frame, text=info_text, font=("Segoe UI", 9), wraplength=550, justify="left", foreground="#555555")\
    .grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

# Bidder ID Entry
tb.Label(login_frame, text="Bidder ID:").grid(row=1, column=0, sticky="e", padx=6)
username_entry = tb.Entry(login_frame, width=41)
username_entry.grid(row=1, column=1, sticky="w")
add_placeholder(username_entry, "Enter your Bidder ID")

bidder_username = tk.StringVar()

# ================= MAIN BIDDER FRAME =================
main_frame = tb.Frame(app)

# ---- Auction List
auction_list_frame = tb.Labelframe(main_frame, text="Live Auctions", padding=10)
auction_list_frame.pack(fill="both", expand=True, padx=15, pady=10)

auction_log = ScrolledText(auction_list_frame, autohide=True)
auction_log.pack(fill="both", expand=True)
auction_log.text.configure(state="disabled", wrap="word")

# ---- Place Bid Frame
bid_frame = tb.Labelframe(main_frame, text="Place a Bid", padding=10)
bid_frame.pack(fill="x", padx=15, pady=5)

tb.Label(bid_frame, text="Item ID:").grid(row=0, column=0, sticky="e", padx=6)
bid_item_id = tb.Entry(bid_frame, width=10)
bid_item_id.grid(row=0, column=1, sticky="w")
add_placeholder(bid_item_id, "Item ID")

tb.Label(bid_frame, text="Bid Amount:").grid(row=0, column=2, sticky="e", padx=6)
bid_amount = tb.Entry(bid_frame, width=15)
bid_amount.grid(row=0, column=3, sticky="w")
add_placeholder(bid_amount, "Amount")

# ---- Place Bid Function
def place_bid():
    if not validate_float_entry(bid_amount):
        return
    try:
        item_id = int(bid_item_id.get())
        amount = float(bid_amount.get())
    except ValueError:
        show_error("Invalid Input", "Item ID must be a number")
        return
    req = {"action": "place_bid", "item_id": item_id, "bidder": bidder_username.get(), "amount": amount}
    res = send_request(req)
    if res.get("status") == "ok":
        show_info("Bid Placed", res.get("message", "Bid successful"))
    else:
        show_error("Bid Failed", res.get("message", "Failed to place bid"))

tb.Button(bid_frame, text="Place Bid", bootstyle="primary", width=15, command=place_bid).grid(row=0, column=4, padx=5)
tb.Button(bid_frame, text="Help / Guide", bootstyle="info", width=15, command=show_help_guide).grid(row=0, column=5, padx=5)

# ================= LOGIN FUNCTION =================
def login():
    user = username_entry.get().strip()
    if not user or user == "Enter your Bidder ID":
        show_error("Login Failed", "Please enter a valid Bidder ID")
        return
    bidder_username.set(user)
    bidder_label.config(text=f"Bidder: {user}")
    login_frame.pack_forget()
    main_frame.pack(expand=True, fill="both")
    Thread(target=refresh_auctions_loop, daemon=True).start()
    show_info("Welcome", f"Logged in as {user}")

tb.Button(login_frame, text="Login", bootstyle="success", width=20, command=login).grid(row=2, column=1, pady=10)

# ================= LIVE AUCTION REFRESH =================
def refresh_auctions_loop():
    while True:
        time.sleep(REFRESH_INTERVAL)
        res = send_request({"action": "get_auctions"})
        if res.get("status") != "ok":
            continue
        # items = res.get("auctions", [])
        items = sorted(res.get("auctions", []), key=lambda x: x.get("item_id", 0), reverse=True)


        def update_ui():
            auction_log.text.configure(state="normal")
            auction_log.text.delete("1.0", "end")

            for item in items:

                # 🔒 Hide private auctions from bidders
                if not item.get("public"):
                    continue

                item_id = item.get("item_id", "N/A")
                name = item.get("name", "Unnamed Item")
                current_bid = item.get("current_bid", 0)
                highest_bidder = item.get("highest_bidder") or "None"
                description = item.get("description", "")

                status = item.get("status", "N/A")

                # Always initialize
                winner_text = ""

                last_status = auction_last_status.get(item_id)

                # 🏁 Auction JUST closed (ACTIVE → CLOSED)
                if last_status == "ACTIVE" and status == "CLOSED" and highest_bidder != "None":
                    winner_text = f" | Winner: {highest_bidder}"

                    # 🎉 Notify ONLY if this bidder won
                    if highest_bidder == bidder_username.get() and item_id not in shown_wins:
                        shown_wins.add(item_id)

                        def notify_win(n=name, i=item_id):
                            show_info(
                                "🎉 Auction Won!",
                                f"Congratulations! You won auction '{n}' (ID {i})"
                            )

                        app.after(0, notify_win)

                # 🔁 Update last known status
                auction_last_status[item_id] = status


                start_time = item.get("start_time") or "N/A"
                end_time = item.get("end_time") or "N/A"
                public = "Yes" if item.get("public") else "No"
                auto_extend = "Yes" if item.get("auto_extend") else "No"

                header_tag = f"item_{item_id}"
                auction_log.text.insert("end", f"[ID {item_id}] {name}\n", header_tag)
                auction_log.text.tag_config(header_tag, foreground="black", font=("Segoe UI", 12, "bold"))

                auction_log.text.insert("end", f"   Current Bid: {CURRENCY_SYMBOL}{current_bid} | Highest Bidder: {highest_bidder}\n")
                auction_log.text.insert("end", f"   Status: {status}{winner_text} | Start: {start_time} | End: {end_time} | Public: {public} | Auto Extend: {auto_extend}\n")

                if description:
                    auction_log.text.insert("end", f"   Description: {description}\n")
                auction_log.text.insert("end", "\n")

                # Disable bidding inputs if auction is closed
            #     if status == "CLOSED":
            #         bid_item_id.config(state="disabled")
            #         bid_amount.config(state="disabled")
            #     else:
            #         bid_item_id.config(state="normal")
            #         bid_amount.config(state="normal")

            # auction_log.text.configure(state="disabled")

        app.after(0, update_ui)

# ================= START APP =================
app.mainloop()

