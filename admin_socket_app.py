import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.widgets.scrolled import ScrolledText
import socket
import json
import threading
import time
from datetime import datetime

HOST = "127.0.0.1"
PORT = 65432
REFRESH_INTERVAL = 2
CURRENCY_SYMBOL = "$"

# ================= HELPERS =================
def send_request(request):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(request).encode())
            return json.loads(s.recv(65536).decode())
    except Exception as e:
        return {"status": "error", "message": str(e)}

def show_error(title, msg):
    messagebox.showerror(title, msg)

def show_info(title, msg):
    messagebox.showinfo(title, msg)

def parse_optional_float(entry):
    val = entry.get().strip()
    if not val or val.lower() == "optional":
        return None
    try:
        return float(val)
    except ValueError:
        show_error("Invalid Input", "Optional price fields must be numbers")
        return None

def parse_optional_text(entry):
    val = entry.get().strip()
    return val if val else None

def add_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(foreground="grey")

    def clear(_):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.config(foreground="black")

    def restore(_):
        if not entry.get():
            entry.insert(0, text)
            entry.config(foreground="grey")

    entry.bind("<FocusIn>", clear)
    entry.bind("<FocusOut>", restore)

# ================= APP =================
app = tb.Window("Auction Admin Panel", themename="flatly", size=(1300, 620))

# ================= CREATE AUCTION =================
form = tb.Labelframe(app, text="Create Auction", padding=15)
form.pack(fill="x", padx=15, pady=10)

# Row 0: Item Name + Auction Type
tb.Label(form, text="Item Name").grid(row=0, column=0, sticky="w", padx=5, pady=5)
item_name = tb.Entry(form, width=30)
item_name.grid(row=0, column=1, sticky="w", padx=5, pady=5)
add_placeholder(item_name, "Laptop, Vehicle")

tb.Label(form, text="Auction Type").grid(row=0, column=2, sticky="w", padx=5, pady=5)
auction_type = tb.Combobox(form, values=["English"], state="readonly", width=20)
auction_type.grid(row=0, column=3, sticky="w", padx=5, pady=5)
auction_type.set("English")

# Row 1: Starting Bid + Reserve Price
tb.Label(form, text="Starting Bid").grid(row=1, column=0, sticky="w", padx=5, pady=5)
starting_bid = tb.Entry(form, width=22)
starting_bid.grid(row=1, column=1, sticky="w", padx=5, pady=5)
add_placeholder(starting_bid, "0.00")

tb.Label(form, text="Reserve Price").grid(row=1, column=2, sticky="w", padx=5, pady=5)
reserve_price = tb.Entry(form, width=22)
reserve_price.grid(row=1, column=3, sticky="w", padx=5, pady=5)
add_placeholder(reserve_price, "Optional")

# Row 2: Buy Now + Min Increment
tb.Label(form, text="Buy Now").grid(row=2, column=0, sticky="w", padx=5, pady=5)
buy_now = tb.Entry(form, width=22)
buy_now.grid(row=2, column=1, sticky="w", padx=5, pady=5)
add_placeholder(buy_now, "Optional")

tb.Label(form, text="Min Increment").grid(row=2, column=2, sticky="w", padx=5, pady=5)
min_increment = tb.Entry(form, width=22)
min_increment.grid(row=2, column=3, sticky="w", padx=5, pady=5)
add_placeholder(min_increment, "1.00")

# Row 3: Start Time + End Time
tb.Label(form, text="Start Time").grid(row=3, column=0, sticky="w", padx=5, pady=5)
start_time = tb.Entry(form, width=22)
start_time.grid(row=3, column=1, sticky="w", padx=5, pady=5)
add_placeholder(start_time, "YYYY-MM-DD HH:MM")

tb.Label(form, text="End Time").grid(row=3, column=2, sticky="w", padx=5, pady=5)
end_time = tb.Entry(form, width=22)
end_time.grid(row=3, column=3, sticky="w", padx=5, pady=5)
add_placeholder(end_time, "YYYY-MM-DD HH:MM")

# Row 4: Checkbuttons
public_var = tk.BooleanVar(value=True)
auto_extend_var = tk.BooleanVar(value=True)

tb.Checkbutton(form, text="Public Visibility", variable=public_var)\
    .grid(row=4, column=0, pady=5, sticky="w", padx=5)

tb.Checkbutton(form, text="Auto Extend", variable=auto_extend_var)\
    .grid(row=4, column=1, pady=5, sticky="w", padx=5)


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


def create_auction():
    # ----------------- Basic Field Validation -----------------
    name_val = item_name.get().strip()
    if not name_val:
        show_error("Invalid Input", "Item Name cannot be empty.")
        return

    try:
        starting_bid_val = float(starting_bid.get().strip())
        if starting_bid_val < 0:
            raise ValueError
    except ValueError:
        show_error("Invalid Input", "Starting Bid must be a positive number.")
        return

    reserve_price_val = parse_optional_float(reserve_price)
    buy_now_val = parse_optional_float(buy_now)

    try:
        min_increment_val = float(min_increment.get().strip())
        if min_increment_val <= 0:
            raise ValueError
    except ValueError:
        show_error("Invalid Input", "Min Increment must be a number greater than 0.")
        return

    start_time_val = parse_optional_text(start_time)
    end_time_val = parse_optional_text(end_time)

    # ----------------- Validate date/time format -----------------
    dt_format = "%Y-%m-%d %H:%M"
    start_dt = end_dt = None
    if start_time_val:
        try:
            start_dt = datetime.strptime(start_time_val, dt_format)
        except ValueError:
            show_error("Invalid Input", "Start Time must be in YYYY-MM-DD HH:MM format.")
            return
    if end_time_val:
        try:
            end_dt = datetime.strptime(end_time_val, dt_format)
        except ValueError:
            show_error("Invalid Input", "End Time must be in YYYY-MM-DD HH:MM format.")
            return

    if start_dt and end_dt and start_dt >= end_dt:
        show_error("Invalid Input", "End Time must be after Start Time.")
        return

    # ----------------- Build Payload -----------------
    payload = {
        "name": name_val,
        "description": None,
        "type": auction_type.get(),
        "starting_bid": starting_bid_val,
        "reserve_price": reserve_price_val,
        "buy_now": buy_now_val,
        "min_increment": min_increment_val,
        "start_time": start_time_val,
        "end_time": end_time_val,
        "public": public_var.get(),
        "auto_extend": auto_extend_var.get()
    }

    # ----------------- Send Request -----------------
    res = send_request({"action": "create_auction", "payload": payload})
    if res["status"] == "ok":
        show_info("Success", "Auction created successfully.")
    else:
        show_error("Error", res.get("message", "Unknown error occurred."))

# Row 4: Buttons
tb.Button(
    form,
    text="Create Auction",
    bootstyle="success",
    command=create_auction
).grid(row=4, column=2, pady=10, sticky="e", padx=5)

tb.Button(
    form,
    text="Help / Guide",
    bootstyle="info",
    command=show_help_guide
).grid(row=4, column=3, pady=10, sticky="w", padx=5)

    
# ================= LIVE VIEW =================
live = tb.Labelframe(app, text="Live Auctions")
live.pack(fill="both", expand=True, padx=15, pady=10)

log = ScrolledText(live, height=20)
log.pack(fill="both", expand=True)
log.text.config(state="disabled")

def update_status(item_id, status):
    """Send update status request to server"""
    res = send_request({"action": "update_status", "item_id": item_id, "status": status})
    if res["status"] != "ok":
        show_error("Error", f"Failed to update status for item {item_id}: {res['message']}")

def update_public(item_id, public):
    res = send_request({
        "action": "update_public",
        "item_id": item_id,
        "public": public
    })
    if res["status"] != "ok":
        show_error("Error", f"Failed to update public visibility: {res['message']}")
def delete_auction(item_id):
    if not messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to permanently delete auction ID {item_id}?"
    ):
        return

    res = send_request({
        "action": "delete_auction",
        "item_id": item_id
    })

    if res["status"] != "ok":
        show_error("Error", f"Failed to delete auction: {res['message']}")
    else:
        show_info("Deleted", f"Auction ID {item_id} deleted successfully.")

def refresh_loop():
    while True:
        time.sleep(REFRESH_INTERVAL)
        res = send_request({"action": "get_auctions"})
        if res["status"] != "ok":
            continue

        # items = res["auctions"] 
        items = sorted(res["auctions"], key=lambda x: x.get("item_id", 0), reverse=True)

        # Prepare active bidders map (start empty, fill asynchronously)
        bids_map = {a['item_id']: set() for a in items}

        # Function to fetch bidders asynchronously
        def fetch_bidders(item_id):
            try:
                bids_res = send_request({"action": "get_bids", "item_id": item_id})
                active_bidders = set()
                if bids_res.get("status") == "ok":
                    for bid in bids_res.get("bids", []):
                        active_bidders.add(bid["bidder"])
                bids_map[item_id] = active_bidders
            except:
                bids_map[item_id] = set()

        # Launch threads to fetch bidders per auction without blocking GUI
        for a in items:
            threading.Thread(target=fetch_bidders, args=(a['item_id'],), daemon=True).start()

        def update():
            log.text.config(state="normal")
            log.text.delete("1.0", "end")
            now = datetime.now()

            for a in items:
                # Auto-close auction if end_time passed
                end_time_str = a['end_time']
                if end_time_str:
                    try:
                        end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
                        if now >= end_dt and a['status'] == "ACTIVE":
                            update_status(a['item_id'], "CLOSED")
                            a['status'] = "CLOSED"
                    except:
                        pass

                # Auction info
                log.text.insert(
                    "end",
                    f"[ID {a['item_id']}] {a['name']} ({a['type']})\n"
                    f"Current Bid: {CURRENCY_SYMBOL}{a['current_bid']:.2f} | "
                    f"Highest Bidder: {a['highest_bidder'] or 'None'} | "
                    f"Start: {a['start_time'] or 'N/A'} | End: {a['end_time'] or 'N/A'} | "
                    f"Public: {'Yes' if a['public'] else 'No'} | Auto Extend: {'Yes' if a['auto_extend'] else 'No'} | "
                    f"Auto-Bid: {'ON' if a['auto_bidding'] else 'OFF'} | "
                    f"Status: {a['status']}\n"
                )

                # Show active bidders (update from bids_map, may be empty at first)
                active_bidders = bids_map.get(a['item_id'], set())
                bidders_str = ", ".join(active_bidders) if active_bidders else "None"
                log.text.insert("end", f"Active Bidders: {bidders_str}\n")

                # Close/Reopen buttons
                def make_action(item_id, status):
                    return lambda: update_status(item_id, status)

                btn_frame = tk.Frame(log.text)

                # Close / Reopen
                if a['status'] == "ACTIVE":
                    tb.Button(
                        btn_frame,
                        text="Close",
                        bootstyle="danger",
                        command=make_action(a['item_id'], "CLOSED")
                    ).pack(side="left", padx=2)
                else:
                    tb.Button(
                        btn_frame,
                        text="Reopen",
                        bootstyle="success",
                        command=make_action(a['item_id'], "ACTIVE")
                    ).pack(side="left", padx=2)

                # Private/Public buttons
                def make_action_public(item_id, public):
                    return lambda: update_public(item_id, public)

                # Public Yes / No
                if a['public']:
                    tb.Button(
                        btn_frame,
                        text="Make Private",
                        bootstyle="warning",
                        command=make_action_public(a['item_id'], 0)
                    ).pack(side="left", padx=5)
                else:
                    tb.Button(
                        btn_frame,
                        text="Make Public",
                        bootstyle="info",
                        command=make_action_public(a['item_id'], 1)
                    ).pack(side="left", padx=5)

                # Delete 
                def action_delete(item_id):
                    return lambda: delete_auction(item_id)

                # Delete button
                tb.Button(
                    btn_frame,
                    text="Delete",
                    bootstyle="danger-outline",
                    command=action_delete(a['item_id'])
                ).pack(side="left", padx=5)


                log.text.window_create("end", window=btn_frame)
                log.text.insert("end", "\n\n")

            log.text.config(state="disabled")

        # Update GUI
        app.after(0, update)

threading.Thread(target=refresh_loop, daemon=True).start()
app.mainloop()
