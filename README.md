# hsademo

## PROJECT OVERVIEW
This project demonstrates the lifecycle of a Health Savings Account (HSA):
-Create an account
-Deposit funds
-Issue a virtual debit card
-Simulate purchases (approve/decline IRS-qualified medical expenses)

## TECH STACK
backend: FastAPI with Uvicorn
frontend: JavaScript, html, css
database: in-memory store (for demo -> implement database in future vision)

## STARTUP INSTRUCTIONS
1) Clone the repo:
   git clone https://github.com/archisha1223/hsademo.git
   cd hsademo
2) Create virtual environment:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
3) Start the backend:
   uvicorn backend.main:app --reload
5) Start the frontend (in a new terminal window):
   cd frontend
   python3 -m http.server 8080
6) Local endpoints (after you start the servers):
   - Backend docs:  http://localhost:8000/docs
   - Frontend app:  http://localhost:8080/index.html

    Note: These are local-only and won’t open unless you’ve started the backend and frontend as described 
    above. They are not public links.
