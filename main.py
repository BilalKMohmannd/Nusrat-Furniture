import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import plotly.express as px
import os

st.set_page_config(page_title="Nusrat Furniture - Transaction Manager", layout="wide")

# --- Constants ---
CSV_FILE = "transactions.csv"
PIN_CODE = "Nusrat1221"
JOBS = ["Polish Wala", "Driver", "Employee", "Other"]

# --- Load Data ---
def load_data():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=["date", "id", "name", "job", "reason", "amount", "type"])
        df.to_csv(CSV_FILE, index=False)
    return pd.read_csv(CSV_FILE, parse_dates=["date"])

# --- Save Data ---
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# --- Generate or Get Existing ID ---
def get_or_create_id(df, name):
    person = df[df['name'].str.lower() == name.lower()]
    if not person.empty:
        return person.iloc[0]['id']
    return str(uuid.uuid4())[:8]

# --- Add Transaction ---
def add_transaction(date, id_, name, job, reason, amount, type_):
    df = load_data()
    new_data = pd.DataFrame([{
        "date": date,
        "id": id_,
        "name": name,
        "job": job,
        "reason": reason,
        "amount": amount,
        "type": type_
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    save_data(df)
    return True

# --- Filter Data ---
def filter_data(df, name=None, id_=None, job=None, date=None):
    if name:
        df = df[df['name'].str.contains(name, case=False)]
    if id_:
        df = df[df['id'].str.contains(id_, case=False)]
    if job:
        df = df[df['job'].str.contains(job, case=False)]
    if date:
        df = df[df['date'] == pd.to_datetime(date)]
    return df

# --- Style In/Out ---
def color_type(val):
    return f"color: {'green' if val == 'In' else 'red'}"

# --- Login ---
def login_ui():
    st.title("🔐 Nusrat Furniture - Secure Access")
    pin = st.text_input("Enter PIN", type="password")
    if st.button("Login"):
        if pin == PIN_CODE:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid PIN! Please try again.")

# --- App UI ---
def app_ui():
    st.markdown("<h1 style='text-align: center; color: darkblue;'>📘 Nusrat Furniture Transaction Manager</h1>", unsafe_allow_html=True)
    df = load_data()

    # --- Sidebar Search ---
    st.sidebar.header("🔍 Search Filters")
    search_name = st.sidebar.text_input("Search by Name")
    search_id = st.sidebar.text_input("Search by ID")
    search_job = st.sidebar.selectbox("Search by Job", ["", *JOBS])
    search_date = st.sidebar.date_input("Search by Date", value=None)

    filtered_df = filter_data(df, search_name, search_id, search_job if search_job else None, search_date if search_date else None)

    # --- Transaction Form ---
    with st.expander("➕ Add New Transaction"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Person's Name")
            job = st.selectbox("Job Role", JOBS)
            reason = st.text_input("Reason")
            amount = st.number_input("Amount", min_value=0.0)
        with col2:
            type_ = st.selectbox("Type", ["In", "Out"])
            date = st.date_input("Date", value=datetime.today())
            date = pd.to_datetime(date)

        if st.button("💾 Submit Transaction"):
            if name and reason and amount > 0:
                id_ = get_or_create_id(df, name)
                add_transaction(date, id_, name, job, reason, amount, type_)
                st.success(f"Transaction added for {name} ({type_})")
                st.balloons()
                st.rerun()
            else:
                st.warning("Please fill all required fields.")

    # --- Transactions Table ---
    st.subheader("📄 Transactions")
    if filtered_df.empty:
        st.info("No transactions found for the selected filters.")
    else:
        styled_df = filtered_df.style.applymap(color_type, subset=["type"])
        st.dataframe(styled_df, use_container_width=True)

        # --- Totals ---
        total_in = filtered_df[filtered_df['type'] == 'In']['amount'].sum()
        total_out = filtered_df[filtered_df['type'] == 'Out']['amount'].sum()

        st.markdown(f"### 💰 Total Summary")
        st.markdown(f"- ✅ **Total Incoming (In)**: <span style='color:green; font-weight:bold;'>Rs. {total_in:,.2f}</span>", unsafe_allow_html=True)
        st.markdown(f"- ❌ **Total Outgoing (Out)**: <span style='color:red; font-weight:bold;'>Rs. {total_out:,.2f}</span>", unsafe_allow_html=True)

    # --- Summary ---
    st.subheader("📊 Summary Per Person")
    if not filtered_df.empty:
        pivot = filtered_df.pivot_table(index=["name", "job"], columns="type", values="amount", aggfunc="sum", fill_value=0).reset_index()

        if 'In' not in pivot.columns:
            pivot['In'] = 0
        if 'Out' not in pivot.columns:
            pivot['Out'] = 0

        fig = px.bar(pivot, x="name", y=["In", "Out"], barmode="group",
                     color_discrete_map={"In": "green", "Out": "red"},
                     title="In vs Out per Person")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(pivot, use_container_width=True)

    # --- Export Button ---
    st.download_button("📥 Download Full CSV", data=df.to_csv(index=False), file_name="transactions_backup.csv", mime="text/csv")

# --- App Entry ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_ui()
else:
    app_ui()
