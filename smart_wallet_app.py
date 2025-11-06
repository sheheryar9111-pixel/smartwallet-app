# smart_wallet_app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Smart Wallet", layout="wide", initial_sidebar_state="expanded")

# --- Utilities ---
def load_transactions():
    try:
        df = pd.read_csv("transactions.csv", index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["timestamp","type","category","amount","note"])
    return df

def save_transactions(df):
    df.to_csv("transactions.csv")

def add_transaction(t_type, category, amount, note):
    df = load_transactions()
    df.loc[len(df)] = [datetime.now().isoformat(), t_type, category, float(amount), note]
    save_transactions(df)
    return df

def load_profile():
    try:
        p = pd.read_json("profile.json", typ="series")
        return p.to_dict()
    except Exception:
        return {"name":"","email":"","currency":"$","color_mode":"light","accessibility":"off"}

def save_profile(profile):
    pd.Series(profile).to_json("profile.json")

def load_notifications():
    try:
        return pd.read_csv("notifications.csv", index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["time","type","title","body"])
        return df

def push_notification(t, title, body):
    df = load_notifications()
    df.loc[len(df)] = [datetime.now().isoformat(), t, title, body]
    df.to_csv("notifications.csv")

# --- Authentication (simple) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""

# Sidebar navigation
if not st.session_state.logged_in:
    st.sidebar.title("Welcome")
    page = st.sidebar.selectbox("Start", ["Login","Register","About"])
else:
    page = st.sidebar.radio("Menu", ["Dashboard","Add Transaction","Budget","Savings Goals","Investment Advice","Notifications","Profile","Logout"])

# --- Pages ---
if (not st.session_state.logged_in) and page=="About":
    st.title("Smart Wallet — Prototype")
    st.write("Prototype built to match wireframes in your report. Features: transactions, budgets, savings goals, notifications, basic investment suggestions.")
    st.info("Upload your wireframes or request style changes and I will match them.")

if (not st.session_state.logged_in) and page=="Register":
    st.title("Create account")
    name = st.text_input("Full name")
    email = st.text_input("Email")
    if st.button("Register"):
        profile = {"name":name,"email":email,"currency":"$","color_mode":"light","accessibility":"off"}
        save_profile(profile)
        st.success("Account created. Please login.")
        push_notification("info","Welcome","Account created for "+email)

if (not st.session_state.logged_in) and page=="Login":
    st.title("Sign in")
    email = st.text_input("Email")
    if st.button("Sign in"):
        profile = load_profile()
        if email==profile.get("email","") and email!="":
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.success("Logged in as "+email)
        else:
            st.error("No account found. Use Register or enter the same email used during registration.")
            # allow guest quick login
            if st.button("Continue as Guest"):
                st.session_state.logged_in=True
                st.session_state.user_email="guest"
                st.info("Using guest session (data stored locally).")

# Main app pages for logged-in user
if st.session_state.logged_in:
    if page=="Logout":
        st.session_state.logged_in=False
        st.session_state.user_email=""
        st.experimental_rerun()

    profile = load_profile()
    st.header("Smart Wallet")
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader(f"Hello, {profile.get('name','User') or 'User'}")
    with col2:
        st.write("Logged in as:", st.session_state.user_email)

    # Dashboard
    if page=="Dashboard":
        st.markdown("### Financial Overview")
        df = load_transactions()
        if df.empty:
            st.info("No transactions yet — add transactions from the sidebar.")
        else:
            income = df[df["type"]=="Income"]["amount"].sum()
            expense = df[df["type"]=="Expense"]["amount"].sum()
            col1,col2,col3 = st.columns(3)
            col1.metric("Total Income", f"{profile.get('currency','$')}{income:,.2f}")
            col2.metric("Total Expense", f"{profile.get('currency','$')}{expense:,.2f}")
            col3.metric("Net", f"{profile.get('currency','$')}{income-expense:,.2f}")
            if income>0:
                st.progress(min(expense/income,1.0))
            st.markdown("#### Spending by Category")
            cat = df[df["type"]=="Expense"].groupby("category")["amount"].sum()
            if not cat.empty:
                st.bar_chart(cat)
            st.markdown("#### Recent Transactions")
            st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True).head(20))

    # Add Transaction
    if page=="Add Transaction":
        st.markdown("### Add Income or Expense")
        t_type = st.selectbox("Type", ["Income","Expense"])
        category = st.text_input("Category (e.g., Food, Rent)")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        note = st.text_input("Note (optional)")
        if st.button("Add"):
            add_transaction(t_type, category or "Uncategorized", amount, note)
            push_notification("warning" if t_type=="Expense" and amount>100 else "info", f"New {t_type}", f"{category} {amount}")
            st.success("Transaction added.")

    # Budget
    if page=="Budget":
        st.markdown("### Budget Checker")
        budget = st.number_input("Monthly budget ($)", min_value=0.0, format="%.2f")
        df = load_transactions()
        month = pd.to_datetime(df["timestamp"]).dt.to_period("M") if not df.empty else None
        this_month = datetime.now().strftime("%Y-%m")
        spent = 0.0
        if not df.empty:
            df["ym"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m")
            spent = df[(df["ym"]==this_month) & (df["type"]=="Expense")]["amount"].sum()
        st.write(f"Spent this month: {profile.get('currency','$')}{spent:,.2f}")
        if st.button("Check"):
            if spent>budget and budget>0:
                st.error("⚠️ You are overspending this month.")
                push_notification("alert","Overspending","You exceeded your set budget.")
            else:
                st.success("🎉 Within budget.")

    # Savings Goals
    if page=="Savings Goals":
        st.markdown("### Savings Goal Tracker")
        goal = st.number_input("Goal amount ($)", min_value=0.0, format="%.2f")
        saved = st.number_input("Amount saved so far ($)", min_value=0.0, format="%.2f")
        if goal>0:
            st.progress(min(saved/goal,1.0))
            st.write(f"{saved/goal*100 if goal>0 else 0:.2f}% achieved")
        if st.button("Save Goal"):
            push_notification("info","Goal set", f"Goal {goal} saved amount {saved}")
            st.success("Goal saved (local).")

    # Investment Advice
    if page=="Investment Advice":
        st.markdown("### Simple Investment Suggestions")
        df = load_transactions()
        balance = df[df["type"]=="Income"]["amount"].sum() - df[df["type"]=="Expense"]["amount"].sum()
        st.write(f"Estimated balance: {profile.get('currency','$')}{balance:,.2f}")
        st.write("- Consider allocating 20% of monthly surplus to low-risk mutual funds.")
        st.write("- Keep an emergency fund equal to 3 months of expenses.")
        if st.button("Get tailored suggestion"):
            if balance>1000:
                st.success("Suggested: 20% to mutual funds, 10% to short-term deposits.")
            else:
                st.info("Suggested: Build emergency savings first.")

    # Notifications
    if page=="Notifications":
        st.markdown("### Notifications")
        n = load_notifications()
        if n.empty:
            st.info("No notifications yet.")
        else:
            st.table(n.sort_values("time", ascending=False).reset_index(drop=True))

    # Profile
    if page=="Profile":
        st.markdown("### Profile & Settings")
        name = st.text_input("Full name", profile.get("name",""))
        email = st.text_input("Email", profile.get("email",""))
        currency = st.selectbox("Currency symbol", ["$","£","€","AED"], index=0)
        if st.button("Save Profile"):
            profile_new = {"name":name,"email":email,"currency":currency,"color_mode":profile.get("color_mode"),"accessibility":profile.get("accessibility")}
            save_profile(profile_new)
            st.success("Profile saved.")

    # End main
    st.markdown("---")
    st.caption("Prototype based on supplied wireframes and system design.")
