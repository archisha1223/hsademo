from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# Pydantic handles request validation automatically
from random import randint
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HSA Login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

users = []
accounts = []
user_counter = 1
account_counter = 1

# Account Creation
class UserCreate(BaseModel):
    name: str
    email: str

@app.post("/api/users")
def create_user(payload: UserCreate):
    global user_counter, account_counter

    # Create a new user object
    user = {
        "id": user_counter,
        "name": payload.name,
        "email": payload.email,
    }
    users.append(user)

    # Create a new HSA account for this user
    account = {
        "id": account_counter,
        "user_id": user_counter,
        "balance": 0.0
    }
    accounts.append(account)

    # Increment counters for next creation
    user_counter += 1
    account_counter += 1

    return {
        "user_id": user["id"],
        "account_id": account["id"],
        "balance": account["balance"]
    }

# Deposit Funds
class DepositRequest(BaseModel):
    account_id: int
    amount: float  

@app.post("/api/deposits")
def deposit_funds(payload: DepositRequest):
    # Find the account
    account = next((acc for acc in accounts if acc["id"] == payload.account_id), None)
    if not account:
        return {"error": "Account not found"}

    # Update the balance
    account["balance"] += payload.amount

    return {
        "account_id": account["id"],
        "new_balance": account["balance"]
    }

# Issue a Card
class CardRequest(BaseModel):
    account_id: int

# Simple in-memory cards list
cards = []
card_counter = 1

@app.post("/api/cards")
def issue_card(payload: CardRequest):
    global card_counter

    # Find the account
    account = next((acc for acc in accounts if acc["id"] == payload.account_id), None)
    if not account:
        return {"error": "Account not found"}

    # Check if a card already exists for this account
    existing_card = next((c for c in cards if c["account_id"] == account["id"]), None)
    if existing_card:
        return {
            "message": "Card already issued",
            "card_id": existing_card["id"],
            # masked card number bc it prevents full card nums from being exposed
            "masked_pan": existing_card["masked_pan"]
        }

    # Generate last 4 digits randomly
    last4 = f"{randint(1000, 9999)}"
    masked_pan = f"4111 **** **** {last4}"

    # Generate CVV
    cvv = f"{randint(100, 999)}"

    # Create the card object
    card = {
        "id": card_counter,
        "account_id": account["id"],
        "masked_pan": masked_pan,
        "last4": last4,
        "exp_month": 12,
        "exp_year": 2029,
        "cvv": cvv
    }
    cards.append(card)
    card_counter += 1

    return {
        "card_id": card["id"],
        "account_id": account["id"],
        "masked_pan": card["masked_pan"],
        "cvv": card["cvv"],
        "exp_date": f"{card['exp_month']}/{card['exp_year']}"
    }

# Validate Transactions
# mcc = merchant category codes
# 5912 = drug stores and pharmacies, 8021 = dentists/ortho
# 8042 = Optometrists, Ophthalmologists, 5411 = grocery
merchants = [
    {"id": 1, "name": "CVS Pharmacy", "mcc": "5912", "category": "Pharmacy"},
    {"id": 2, "name": "Freeman Dental", "mcc": "8021", "category": "Dental"},
    {"id": 3, "name": "Vision Center", "mcc": "8042", "category": "Optometry"},
    {"id": 4, "name": "Walmart", "mcc": "5411", "category": "Grocery"},
    {"id": 5, "name": "City Hospital", "mcc": "8062", "category": "Hospital"},
    {"id": 6, "name": "Family Clinic", "mcc": "8011", "category": "Physician"},
    {"id": 7, "name": "Back Care Chiropractic", "mcc": "8041", "category": "Chiropractor"},
    {"id": 8, "name": "Quest Diagnostics", "mcc": "8071", "category": "Lab Tests"},
    {"id": 9, "name": "EMS Ambulance", "mcc": "4119", "category": "Ambulance"},
    {"id": 10, "name": "BlueShield Insurance", "mcc": "6300", "category": "Insurance"},
    {"id": 11, "name": "Amazon.com", "mcc": "5942", "category": "Online Retail"},
    {"id": 12, "name": "Best Buy", "mcc": "5732", "category": "Electronics"},
    {"id": 13,"name": "Whole Foods Market", "mcc": "5411", "category": "Grocery"},
    {"id": 14,"name": "Target", "mcc": "5411", "category": "General Retail"},
    {"id": 15,"name": "Planet Fitness", "mcc": "7997", "category": "Gym Membership"},
]

QUALIFIED_MCC = {
    "5912", "8021", "8042", "8011", "8062", "8041", "8071", "4119", "6300"
} 

transactions = []
txn_counter = 1

@app.get("/api/merchants")
def get_merchants():
    return merchants

class PurchaseRequest(BaseModel):
    account_id: int
    card_id: int
    merchant_id: int
    amount: float

@app.post("/api/purchase")
def purchase(payload: PurchaseRequest):
    global txn_counter

    # basic input checks
    if payload.amount <= 0:
        return {"error": "INVALID_AMOUNT"}

    account = next((a for a in accounts if a["id"] == payload.account_id), None)
    if not account:
        return {"error": "INVALID_ACCOUNT"}

    # card must exist and belong to this account
    card = next((c for c in cards if c["id"] == payload.card_id and c["account_id"] == account["id"]), None)
    if not card:
        return {"error": "INVALID_CARD"}

    merchant = next((m for m in merchants if m["id"] == payload.merchant_id), None)
    if not merchant:
        return {"error": "INVALID_MERCHANT"}

    qualified = merchant["mcc"] in QUALIFIED_MCC

    status = "APPROVED"
    decline_reason = None

    if not qualified:
        status = "DECLINED"
        decline_reason = "NON_QUALIFIED_EXPENSE"
    elif account["balance"] < payload.amount:
        status = "DECLINED"
        decline_reason = "INSUFFICIENT_FUNDS"
    else:
        # approve: debit the account
        account["balance"] -= payload.amount

    txn = {
        "id": txn_counter,
        "account_id": account["id"],
        "card_id": card["id"],
        "merchant_id": merchant["id"],
        "merchant_name": merchant["name"],
        "amount": payload.amount,
        "status": status,
        "decline_reason": decline_reason,
    }
    transactions.append(txn)
    txn_counter += 1

    return {
        "transaction_id": txn["id"],
        "status": status,
        "decline_reason": decline_reason,
        "new_balance": account["balance"],
    }

@app.get("/api/accounts/{account_id}")
def account_summary(account_id: int):
    account = next((a for a in accounts if a["id"] == account_id), None)
    if not account:
        return {"error": "Account not found"}
    card = next((c for c in cards if c["account_id"] == account_id), None)
    recent = [t for t in transactions if t["account_id"] == account_id][-20:]
    return {
        "account_id": account_id,
        "balance": account["balance"],
        "card": (
            {"id": card["id"], "masked_pan": card["masked_pan"], "exp_date": f"{card['exp_month']}/{card['exp_year']}"}
            if card else None
        ),
        "transactions": recent,
    }
