const API = "http://127.0.0.1:8000/api";

// elements
const el = (id) => document.getElementById(id);
const btnCreate = el("btnCreate");
const btnDeposit = el("btnDeposit");
const btnIssueCard = el("btnIssueCard");
const btnPurchase = el("btnPurchase");
const btnSummary = el("btnSummary");

// bootstrap merchants on load
window.addEventListener("load", async () => {
  try {
    const res = await fetch(`${API}/merchants`);
    const merchants = await res.json();
    const sel = el("merchantSelect");
    sel.innerHTML = "";
    merchants.forEach(m => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = `${m.name} (MCC ${m.mcc})`;
      sel.appendChild(opt);
    });
  } catch (e) {
    el("purchaseOut").textContent = "Could not load merchants. Did you add the /api/merchants endpoint?";
  }
});

// 1) Create user + account
btnCreate.onclick = async () => {
  const name = el("name").value.trim();
  const email = el("email").value.trim();
  if (!name || !email) {
    el("createOut").textContent = "Please enter name and email.";
    return;
  }
  btnCreate.disabled = true;
  try {
    const r = await fetch(`${API}/users`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ name, email })
    });
    const j = await r.json();
    el("createOut").textContent = JSON.stringify(j, null, 2);

    // autofill downstream fields
    if (j.account_id) {
      el("accountIdDeposit").value = j.account_id;
      el("accountIdCard").value = j.account_id;
      el("accountIdBuy").value = j.account_id;
      el("accountIdSummary").value = j.account_id;
    }
  } catch (e) {
    el("createOut").textContent = "Error creating user.";
  } finally {
    btnCreate.disabled = false;
  }
};

// 2) Deposit funds
btnDeposit.onclick = async () => {
  const account_id = parseInt(el("accountIdDeposit").value, 10);
  const amount = parseFloat(el("amountDeposit").value);
  if (!account_id || isNaN(amount)) {
    el("depositOut").textContent = "Enter valid account ID and amount.";
    return;
  }
  btnDeposit.disabled = true;
  try {
    const r = await fetch(`${API}/deposits`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ account_id, amount })
    });
    const j = await r.json();
    el("depositOut").textContent = JSON.stringify(j, null, 2);
  } catch (e) {
    el("depositOut").textContent = "Error depositing funds.";
  } finally {
    btnDeposit.disabled = false;
  }
};

// 3) Issue card
btnIssueCard.onclick = async () => {
  const account_id = parseInt(el("accountIdCard").value, 10);
  if (!account_id) {
    el("cardOut").textContent = "Enter a valid account ID.";
    return;
  }
  btnIssueCard.disabled = true;
  try {
    const r = await fetch(`${API}/cards`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ account_id })
    });
    const j = await r.json();
    el("cardOut").textContent = JSON.stringify(j, null, 2);

    if (j.card_id) {
      el("cardIdBuy").value = j.card_id;
    }
  } catch (e) {
    el("cardOut").textContent = "Error issuing card.";
  } finally {
    btnIssueCard.disabled = false;
  }
};

// 4) Purchase
btnPurchase.onclick = async () => {
  const account_id = parseInt(el("accountIdBuy").value, 10);
  const card_id = parseInt(el("cardIdBuy").value, 10);
  const merchant_id = parseInt(el("merchantSelect").value, 10);
  const amount = parseFloat(el("amountBuy").value);
  if (!account_id || !card_id || !merchant_id || isNaN(amount)) {
    el("purchaseOut").textContent = "Enter account, card, merchant, and amount.";
    return;
  }
  btnPurchase.disabled = true;
  try {
    const r = await fetch(`${API}/purchase`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ account_id, card_id, merchant_id, amount })
    });
    const j = await r.json();
    const statusStr = j.status === "APPROVED"
      ? `✅ APPROVED • New Balance: $${Number(j.new_balance ?? 0).toFixed(2)}`
      : `❌ DECLINED • Reason: ${j.decline_reason}`;
    el("purchaseOut").textContent = `${statusStr}\n\n` + JSON.stringify(j, null, 2);
  } catch (e) {
    el("purchaseOut").textContent = "Error making purchase.";
  } finally {
    btnPurchase.disabled = false;
  }
};

// Summary
btnSummary.onclick = async () => {
  const account_id = parseInt(el("accountIdSummary").value, 10);
  if (!account_id) {
    el("summaryOut").textContent = "Enter a valid account ID.";
    return;
  }
  btnSummary.disabled = true;
  try {
    const r = await fetch(`${API}/accounts/${account_id}`);
    const j = await r.json();
    el("summaryOut").textContent = JSON.stringify(j, null, 2);
  } catch (e) {
    el("summaryOut").textContent = "Error fetching summary.";
  } finally {
    btnSummary.disabled = false;
  }
};