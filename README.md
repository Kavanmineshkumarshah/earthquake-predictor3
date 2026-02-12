# Auction Management System (Full Source)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Architecture](https://img.shields.io/badge/Architecture-Client%20Server-orange)](#)
[![License](https://img.shields.io/badge/License-Commercial-red)](#)

Auction Management System is a modular, socket-based Python application for creating, managing, and participating in real-time online auctions.  
It features a dedicated server, an Admin GUI for auction control, and a Bidder GUI for live participation, all communicating via JSON over TCP sockets.

This repository contains the **full working source code** as a single, self-contained system designed for learning, demonstration, and real-world extension.

------------------------------------------------------------
🌟 FEATURES
------------------------------------------------------------

- 🧾 Bid Management
  - Create and publish auctions
  - Manual bidding with validation
  - Bid history tracking
  - Automatic highest-bid enforcement

- 🏷️ Auction Types
  - English-style auctions (highest bid wins)
  - Easily extensible to other auction models

- ⏱️ Timing & Automation
  - Start and end scheduling
  - Auto-close auctions on expiration
  - Auto-extend (anti-sniping) near auction end
  - Minimum bid increments
  - Server-side auto-bidding (proxy bidding)

- 👥 User Roles
  - Admin panel for auction management
  - Bidder panel for participation
  - Lightweight bidder identity system (ID-based)

- 🔍 Transparency & Visibility
  - Public / private auction visibility
  - Real-time bid visibility
  - Bid history per auction
  - Highest bidder tracking

- 🔔 Live Updates
  - Socket-based real-time refresh
  - Admin and bidder views auto-update
  - Winner notification popup for bidders

- 🗄️ Persistence
  - SQLite database (auctions + bids)
  - Safe deletion and status control
  - Thread-safe operations

------------------------------------------------------------
📁 PROJECT STRUCTURE
------------------------------------------------------------

auction_management_system/
│
├── server.py                  # Auction server (socket + SQLite)
├── admin_socket_app.py        # Admin GUI (Tkinter + ttkbootstrap)
├── bidder_socket_app.py       # Bidder GUI (Tkinter + ttkbootstrap)
├── auctions.db                # SQLite database (auto-created)
└── README.md                  # Project documentation

> Note:  
> This project is intentionally kept simple and flat for clarity.  
> It can be refactored into packages (`client/`, `server/`) for larger deployments.

------------------------------------------------------------
## 💖 Support This Project
------------------------------------------------------------

If these tools save you time or help you learn, consider sponsoring ❤️  

Your support helps me:  
- Maintain and improve tools  
- Add more automation scripts  
- Curate high-quality Python project ideas  

Even **$3/month** makes a difference.  
👉 Click the **Sponsor** button at the top  

------------------------------------------------------------
🚀 INSTALLATION
------------------------------------------------------------

1. Clone the repository:

git clone https://github.com/rogers-cyber/auction-management-system.git  
cd auction-management-system

2. Install required Python packages:

pip install ttkbootstrap

> Tkinter, socket, threading, sqlite3, json are included in the Python standard library.

------------------------------------------------------------
▶️ RUNNING THE SYSTEM
------------------------------------------------------------

1. Start the auction server:

python server.py

2. Start the Admin Panel (in a new terminal):

python admin_socket_app.py

3. Start the Bidder Panel (in another terminal):

python bidder_socket_app.py

------------------------------------------------------------
📌 NOTE: Admin Panel
------------------------------------------------------------

The Admin GUI allows you to:

- Create auctions with:
  - Starting bid
  - Reserve price
  - Buy-now price
  - Minimum increment
  - Start / end time
  - Public or private visibility
  - Auto-extend behavior
- View live auctions
- Close or reopen auctions
- Toggle public/private visibility
- Delete closed auctions
- Monitor active bidders and auto-bids

------------------------------------------------------------
📌 NOTE: Bidder Panel
------------------------------------------------------------

The Bidder GUI allows users to:

- Log in using a custom Bidder ID
- View live public auctions
- Place manual bids
- Track current bids and highest bidders
- Receive a popup notification when they win an auction
- Automatically disable bidding on closed auctions

------------------------------------------------------------
💡 USAGE
------------------------------------------------------------

1. Admin Workflow
   - Launch Admin Panel
   - Create one or more auctions
   - Monitor bids in real time
   - Close auctions manually or let them auto-close

2. Bidder Workflow
   - Launch Bidder Panel
   - Log in with a Bidder ID
   - Watch live auctions
   - Place bids
   - Get notified upon winning

3. Auto-Bidding
   - Auto-bid logic runs server-side
   - Automatically increases bids up to a max limit
   - Prevents last-second sniping when auto-extend is enabled

------------------------------------------------------------
⚙️ CONFIGURATION OPTIONS
------------------------------------------------------------

Option               Description
-------------------  ----------------------------------------------
HOST                 Server IP address (default: 127.0.0.1)
PORT                 Server port (default: 65432)
REFRESH_INTERVAL     Client refresh rate (seconds)
AUTO_EXTEND_MINUTES  Extension window before auction end
TIME_FORMAT          Auction date/time format
Visibility           Public or private auctions
Min Increment        Minimum bid increase

------------------------------------------------------------
📦 DEPENDENCIES
------------------------------------------------------------

- Python 3.8+
- Tkinter (standard library)
- ttkbootstrap
- SQLite3
- socket
- threading
- json
- datetime

------------------------------------------------------------
📝 NOTES
------------------------------------------------------------

- Designed for clarity, learning, and extensibility
- Fully functional real-time socket architecture
- Safe multi-threaded server design
- Ideal for:
  - Educational demos
  - Coursework
  - Internal tools
  - Prototyping auction platforms

------------------------------------------------------------
👤 ABOUT
------------------------------------------------------------

Auction Management System is built for developers and learners who want a **real, working example** of:

- Client–server architecture
- Socket programming in Python
- GUI development with Tkinter
- Real-time data synchronization
- Persistent storage with SQLite

------------------------------------------------------------
📜 LICENSE
------------------------------------------------------------

This project is distributed as **commercial source code**.

You may:
- Use it for personal or commercial projects
- Modify and extend the code

You may NOT:
- Redistribute or resell it as a competing product
- Claim authorship of the original system

------------------------------------------------------------
© Mate Technologies
https://github.com/rogers-cyber

