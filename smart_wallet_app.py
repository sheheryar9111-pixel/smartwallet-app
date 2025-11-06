import streamlit as st
import pandas as pd

# App configuration
st.set_page_config(page_title="Smart Wallet App", layout="wide")

# Title and subtitle
st.title("💰 Smart Wallet App")
st.subheader("Personal Finance Management Prototype")

# Sidebar navigation
menu = ["Dashboard", "Add Transaction", "Budget", "Savings Goals", "Investment Advice"]
choice = st.sidebar.selectbox("Menu", menu)

# Data storage (in memory)
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=["Type", "Category", "Amount"])

# Add Transaction Page
if choice == "Add Transaction":
    st.header("Add Income or Expense")
    t_type = st.selectbox("Type", ["Income", "Expense"])
    category = st.text_input("Category (e.g., Food, Rent)")
    amount = st.number_input("Amount", min_value=0.0)
    if st.button("Add Transaction"):
        new_row = pd.DataFrame([[t_type, category, amount]], columns=["Type", "Category", "Amount"])
        st.session_state.transactions = pd.concat([st.session_state.transactions, new_row], ignore_index=True)
        st.success("✅ Transaction added successfully!")

# Dashboard Page
elif choice == "Dashboard":
    st.header("Financial Overview")
    if not st.session_state.transactions.empty:
        income = st.session_state.transactions[st.session_state.transactions["Type"] == "Income"]["Amount"].sum()
        expense = st.session_state.transactions[st.session_state.transactions["Type"] == "Expense"]["Amount"].sum()

        st.metric("Total Income", f"${income:.2f}")
        st.metric("Total Expense", f"${expense:.2f}")

        if income > 0:
            st.progress(expense / income)
        st.bar_chart(st.session_state.transactions.groupby("Category")["Amount"].sum())
    else:
        st.info("No transactions added yet.")

# Budget Page
elif choice == "Budget":
    st.header("Monthly Budget Checker")
    budget = st.number_input("Enter your budget limit ($):", min_value=0.0)
    if st.button("Check Spending"):
        total_expense = st.session_state.transactions[st.session_state.transactions["Type"] == "Expense"]["Amount"].sum()
        if total_expense > budget:
            st.error("⚠️ Overspending Alert! You've exceeded your budget.")
        else:
            st.success("✅ You're within your budget limits!")

# Savings Goals Page
elif choice == "Savings Goals":
    st.header("Track Your Savings Goal")
    goal = st.number_input("Set Your Goal Amount ($):", min_value=0.0)
    saved = st.number_input("Amount Saved So Far ($):", min_value=0.0)
    progress = saved / goal if goal > 0 else 0
    st.progress(progress)
    st.write(f"🎯 Progress: {progress*100:.2f}% of your goal reached!")

# Investment Advice Page
elif choice == "Investment Advice":
    st.header("💹 Basic Investment Suggestions")
    st.info("Based on your financial habits, here are simple suggestions:")
    st.markdown("""
    - 📈 **Invest 20%** of savings in low-risk mutual funds  
    - 🏦 **Keep 10%** in emergency cash or short-term deposits  
    - 💰 **Explore bonds or ETFs** for stable, long-term growth  
    """)
    st.caption("⚠️ This is not professional financial advice. It's for educational demo purposes only.")
