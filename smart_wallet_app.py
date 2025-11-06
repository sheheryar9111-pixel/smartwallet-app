# smart_wallet_app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os, json

st.set_page_config(page_title="Smart Wallet", layout="wide")

DATA_TX = "transactions.csv"
DATA_NOTIF = "notifications.csv"
PROFILE_FILE = "profile.json"

# --- Storage helpers ---
def load_transactions():
    if os.path.exists(DATA_TX):
        df = pd.read_csv(DATA_TX, index_col=0)
    else:
        df = pd.DataFrame(columns=["timestamp","type","category","amount","note"])
    return df

def save_transactions(df):
    df.to_csv(DATA_TX)

def add_transaction(t_type, category, amount, note):
    df = load_transactions()
    df.loc[len(df)] = [datetime.now().isoformat(), t_type, category, float(amount), note]
    save_transactions(df)

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE,"r") as f:
            return json.load(f)
    return {"name":"User","currency":"$","color_mode":"light"}

def save_profile(p):
    with open(PROFILE_FILE,"w") as f:
        json.dump(p,f)

def load_notifications():
    if os.path.exists(DATA_NOTIF):
        return pd.read_csv(DATA_NOTIF, index_col=0)
    return pd.DataFrame(columns=["time","type","title","body"])

def push_notification(t, title, body):
    n = load_notifications()
    n.loc[len(n)] = [datetime.now().isoformat(), t, title, body]
    n.to_csv(DATA_NOTIF)

# --- Initialize ---
profile = load_profile()

# --- UI ---
st.title("💰 Smart Wallet — Prototype")
st.caption("Working prototype matching your wireframes — no sign-in required. Data saved to CSV.")

menu = st.sidebar.selectbox("Menu", ["Dashboard","Add Transaction","Budget","Savings Goals","Investment Advice","Notifications","Profile","Export CSV"])

# --- Pages ---
if menu == "Dashboard":
    st.header("Financial Overview")
    df = load_transactions()
    if df.empty:
        st.info("No transactions yet. Add one on the 'Add Transaction' page.")
    else:
        income = df[df["type"]=="Income"]["amount"].sum()
        expense = df[df["type"]=="Expense"]["amount"].sum()
        c1,c2,c3 = st.columns(3)
        c1.metric("Total Income", f"{profile['currency']}{income:,.2f}")
        c2.metric("Total Expense", f"{profile['currency']}{expense:,.2f}")
        c3.metric("Net", f"{profile['currency']}{income-expense:,.2f}")
        if income>0:
            st.progress(min(expense/income,1.0))
        st.subheader("Spending by Category")
        cat = df[df["type"]=="Expense"].groupby("category")["amount"].sum()
        if not cat.empty:
            st.bar_chart(cat)
        st.subheader("Recent Transactions")
        st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True).head(20))

elif menu == "Add Transaction":
    st.header("Add Income / Expense")
    t = st.radio("Type", ["Income","Expense"], horizontal=True)
    cat = st.text_input("Category", value="General")
    amt = st.number_input("Amount", min_value=0.0, format="%.2f")
    note = st.text_input("Note (optional)")
    if st.button("Add Transaction"):
        if amt <= 0:
            st.error("Enter amount > 0")
        else:
            add_transaction(t, cat, amt, note)
            if t=="Expense" and amt>100:
                push_notification("alert","Large expense", f"{cat} {profile['currency']}{amt:.2f}")
            st.success("Transaction added")

elif menu == "Budget":
    st.header("Monthly Budget Checker")
    budget = st.number_input("Set monthly budget", min_value=0.0, format="%.2f")
    df = load_transactions()
    this_month = datetime.now().strftime("%Y-%m")
    spent = 0.0
    if not df.empty:
        df["ym"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m")
        spent = df[(df["ym"]==this_month) & (df["type"]=="Expense")]["amount"].sum()
    st.write(f"Spent this month: {profile['currency']}{spent:,.2f}")
    if st.button("Check"):
        if budget>0 and spent>budget:
            st.error("⚠️ Overspending this month")
            push_notification("alert","Overspending","You exceeded your budget")
        else:
            st.success("✅ Within budget")

elif menu == "Savings Goals":
    st.header("Savings Goal Tracker")
    goal = st.number_input("Goal amount", min_value=0.0, format="%.2f")
    saved = st.number_input("Saved so far", min_value=0.0, format="%.2f")
    if goal>0:
        st.progress(min(saved/goal,1.0))
        st.write(f"{saved/goal*100:.2f}% reached")
    if st.button("Set Goal"):
        push_notification("info","Goal set", f"Goal {profile['currency']}{goal:,.2f}, saved {profile['currency']}{saved:,.2f}")
        st.success("Goal recorded (notifications saved)")

elif menu == "Investment Advice":
    st.header("Investment Suggestions")
    df = load_transactions()
    balance = df[df["type"]=="Income"]["amount"].sum() - df[df["type"]=="Expense"]["amount"].sum()
    st.write(f"Estimated balance: {profile['currency']}{balance:,.2f}")
    st.markdown("- Consider 20% to low-risk mutual funds\n- Keep 10% as emergency savings\n- Use bonds/ETFs for stable growth")
    if st.button("Tailored suggestion"):
        if balance>1000:
            st.success("Suggested: 20% mutual funds, 10% short-term deposits")
        else:
            st.info("Suggested: Prioritize emergency savings")

elif menu == "Notifications":
    st.header("Notifications")
    n = load_notifications()
    if n.empty:
        st.info("No notifications")
    else:
        st.table(n.sort_values("time", ascending=False).reset_index(drop=True))

elif menu == "Profile":
    st.header("Profile & Settings")
    name = st.text_input("Name", value=profile.get("name","User"))
    currency = st.selectbox("Currency", ["$","£","€","AED"], index=0)
    if st.button("Save Profile"):
        profile["name"]=name; profile["currency"]=currency
        save_profile(profile)
        st.success("Profile saved")

elif menu == "Export CSV":
    st.header("Export Data")
    df = load_transactions()
    if df.empty:
        st.info("No transactions to export")
    else:
        st.download_button("Download transactions CSV", df.to_csv(index=False), "transactions_export.csv", "text/csv")

st.sidebar.markdown("---")
st.sidebar.write("Prototype based on provided wireframes — no sign-in required.")
