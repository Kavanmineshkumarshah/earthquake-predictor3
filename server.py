import threading
import sqlite3
import socket
import json
import time
from datetime import datetime, timedelta

# ================= CONFIG =================
DB_FILE = "auctions.db"
HOST = "127.0.0.1"
PORT = 65432
REFRESH_INTERVAL = 2

AUTO_EXTEND_MINUTES = 2
TIME_FORMAT = "%Y-%m-%d %H:%M"

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS auctions (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        auction_type TEXT,
        starting_bid REAL,
        current_bid REAL,
        reserve_price REAL,
        buy_now_price REAL,
        min_increment REAL,
        highest_bidder TEXT,
        start_time TEXT,
        end_time TEXT,
        public_visibility INTEGER,
        auto_extend INTEGER,
        status TEXT DEFAULT 'ACTIVE'
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS bids (
        bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        bidder TEXT,
        amount REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# ================= HELPERS =================
def normalize_float(value):
    try:
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None

# ================= DATA ACCESS =================
auto_bids = {}
auto_lock = threading.Lock()

def get_all_auctions():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM auctions ORDER BY item_id")
    rows = c.fetchall()
    conn.close()

    auctions = []
    for r in rows:
        auctions.append({
            "item_id": r[0],
            "name": r[1],
            "description": r[2],
            "type": r[3],
            "starting_bid": r[4],
            "current_bid": r[5],
            "reserve_price": r[6],
            "buy_now": r[7],
            "min_increment": r[8],
            "highest_bidder": r[9],
            "start_time": r[10],
            "end_time": r[11],
            "public": bool(r[12]),
            "auto_extend": bool(r[13]),
            "status": r[14],
            "auto_bidding": r[0] in auto_bids and auto_bids[r[0]]["active"]
        })
    return auctions

def create_auction(payload):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    INSERT INTO auctions (
        name, description, auction_type,
        starting_bid, current_bid,
        reserve_price, buy_now_price,
        min_increment, highest_bidder,
        start_time, end_time,
        public_visibility, auto_extend
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.get("name"),
        payload.get("description"),
        payload.get("type"),
        normalize_float(payload.get("starting_bid")),
        normalize_float(payload.get("starting_bid")),
        normalize_float(payload.get("reserve_price")),
        normalize_float(payload.get("buy_now")),
        normalize_float(payload.get("min_increment")),
        None,
        payload.get("start_time"),
        payload.get("end_time"),
        int(payload.get("public", True)),
        int(payload.get("auto_extend", True))
    ))

    conn.commit()
    conn.close()

# ================= BIDDING =================
def place_bid(item_id, bidder, amount):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
        SELECT current_bid, min_increment, end_time, auto_extend, status
        FROM auctions
        WHERE item_id=?
    """, (item_id,))
    row = c.fetchone()

    if not row:
        conn.close()
        return False, "Auction not found"

    current_bid, min_inc, end_time, auto_extend, status = row

    if status != "ACTIVE":
        conn.close()
        return False, "Auction is closed"

    if amount < current_bid + min_inc:
        conn.close()
        return False, f"Bid must be at least {current_bid + min_inc:.2f}"

    # ================= AUTO EXTEND LOGIC =================
    if auto_extend and end_time:
        try:
            end_dt = datetime.strptime(end_time, TIME_FORMAT)
            now = datetime.now()

            remaining_seconds = (end_dt - now).total_seconds()
            if remaining_seconds <= AUTO_EXTEND_MINUTES * 60:
                end_dt += timedelta(minutes=AUTO_EXTEND_MINUTES)
                end_time = end_dt.strftime(TIME_FORMAT)
        except ValueError:
            pass

    # Update auction
    c.execute("""
        UPDATE auctions
        SET current_bid=?, highest_bidder=?, end_time=?
        WHERE item_id=?
    """, (amount, bidder, end_time, item_id))

    # Insert bid
    c.execute("""
        INSERT INTO bids (item_id, bidder, amount)
        VALUES (?, ?, ?)
    """, (item_id, bidder, amount))

    conn.commit()
    conn.close()
    return True, "Bid placed"

# ================= AUTO-BID =================
def auto_bid_loop(item_id):
    while True:
        time.sleep(REFRESH_INTERVAL)

        with auto_lock:
            if item_id not in auto_bids or not auto_bids[item_id]["active"]:
                return
            bidder = auto_bids[item_id]["bidder"]
            max_bid = auto_bids[item_id]["max_bid"]

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT current_bid, min_increment, highest_bidder FROM auctions WHERE item_id=?", (item_id,))
        row = c.fetchone()

        if not row:
            conn.close()
            return

        current_bid, min_inc, highest_bidder = row
        if current_bid >= max_bid:
            auto_bids[item_id]["active"] = False
            conn.close()
            return

        if highest_bidder != bidder:
            new_bid = min(current_bid + min_inc, max_bid)
            c.execute(
                "UPDATE auctions SET current_bid=?, highest_bidder=? WHERE item_id=?",
                (new_bid, bidder, item_id)
            )
            c.execute(
                "INSERT INTO bids (item_id, bidder, amount) VALUES (?, ?, ?)",
                (item_id, bidder, new_bid)
            )
            conn.commit()

        conn.close()

# ================= SERVER =================
def handle_client(conn, addr):
    try:
        data = conn.recv(65536)
        if not data:
            conn.close()
            return

        try:
            request = json.loads(data.decode())
        except json.JSONDecodeError:
            conn.sendall(json.dumps({"status": "error", "message": "Invalid JSON"}).encode())
            return

        action = request.get("action")
        response = {"status": "error", "message": "Unknown action"}

        if action == "get_auctions":
            response = {"status": "ok", "auctions": get_all_auctions()}

        elif action == "create_auction":
            create_auction(request.get("payload", {}))
            response = {"status": "ok", "message": "Auction created"}

        elif action == "place_bid":
            ok, msg = place_bid(
                request.get("item_id"),
                request.get("bidder"),
                request.get("amount")
            )
            response = {"status": "ok" if ok else "error", "message": msg}

        elif action == "start_auto_bid":
            with auto_lock:
                auto_bids[request["item_id"]] = {
                    "bidder": request["bidder"],
                    "max_bid": request["max_bid"],
                    "active": True
                }
            threading.Thread(
                target=auto_bid_loop,
                args=(request["item_id"],),
                daemon=True
            ).start()
            response = {"status": "ok", "message": "Auto-bid started"}

        elif action == "stop_auto_bid":
            with auto_lock:
                if request["item_id"] in auto_bids:
                    auto_bids[request["item_id"]]["active"] = False
            response = {"status": "ok", "message": "Auto-bid stopped"}

        elif action == "update_status":
            item_id = request.get("item_id")
            new_status = request.get("status")
            if item_id is None or new_status not in ["ACTIVE", "CLOSED"]:
                response = {"status": "error", "message": "Invalid status or item_id"}
            else:
                conn_db = sqlite3.connect(DB_FILE)
                c = conn_db.cursor()
                c.execute("UPDATE auctions SET status=? WHERE item_id=?", (new_status, item_id))
                conn_db.commit()
                conn_db.close()
                response = {"status": "ok", "message": f"Auction {item_id} status updated to {new_status}"}

        elif action == "get_bids":
            item_id = request.get("item_id")
            db_conn = sqlite3.connect(DB_FILE)   # use a different name!
            c = db_conn.cursor()
            c.execute("SELECT bidder, amount, timestamp FROM bids WHERE item_id=?", (item_id,))
            rows = c.fetchall()
            db_conn.close()
            bids = [{"bidder": r[0], "amount": r[1], "timestamp": r[2]} for r in rows]
            response = {"status": "ok", "bids": bids}

        elif action == "update_public":
            item_id = request.get("item_id")
            public = request.get("public")

            if item_id is None or public not in [0, 1, True, False]:
                response = {"status": "error", "message": "Invalid parameters"}
            else:
                conn_db = sqlite3.connect(DB_FILE)
                c = conn_db.cursor()
                c.execute(
                    "UPDATE auctions SET public_visibility=? WHERE item_id=?",
                    (int(public), item_id)
                )
                conn_db.commit()
                conn_db.close()
                response = {"status": "ok", "message": "Public visibility updated"}

        elif action == "delete_auction":
            item_id = request.get("item_id")

            if item_id is None:
                response = {"status": "error", "message": "Missing item_id"}
            else:
                conn_db = sqlite3.connect(DB_FILE)
                c = conn_db.cursor()

                # OPTIONAL SAFETY: block delete if auction is ACTIVE
                c.execute("SELECT status FROM auctions WHERE item_id=?", (item_id,))
                row = c.fetchone()

                if not row:
                    response = {"status": "error", "message": "Auction not found"}
                elif row[0] == "ACTIVE":
                    response = {
                        "status": "error",
                        "message": "Cannot delete an ACTIVE auction. Close it first."
                    }
                else:
                    # Delete bids first (important for FK integrity)
                    c.execute("DELETE FROM bids WHERE item_id=?", (item_id,))
                    c.execute("DELETE FROM auctions WHERE item_id=?", (item_id,))

                    conn_db.commit()
                    response = {"status": "ok", "message": f"Auction {item_id} deleted"}

        # Send JSON response
        conn.sendall(json.dumps(response).encode())

    except Exception as e:
        try:
            conn.sendall(json.dumps({"status": "error", "message": str(e)}).encode())
        except:
            pass  # ignore if sending fails
    finally:
        conn.close()

def start_server():
    init_db()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
