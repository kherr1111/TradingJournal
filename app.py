import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, time
import os

# File to store trades
DATA_FILE = "trades.csv"

# Title
st.title("📈 Trading Performance Dashboard")

# Manual Entry Form
st.sidebar.header("Add New Trade Entry")
with st.sidebar.form("trade_form"):
    date = st.date_input("Date", value=datetime.today())
    trade_time = st.time_input("Time", value=datetime.now().time())
    trade_type = st.selectbox("Trade Type", ["Long", "Short"])
    description = st.text_input("Description")
    pnl = st.number_input("PnL ($)", step=0.01, format="%.2f")
    balance = st.number_input("Balance ($)", step=0.01, format="%.2f")
    submitted = st.form_submit_button("Add Trade")

# Load or create CSV
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=['Date'])
else:
    df = pd.DataFrame(columns=['Date', 'Time', 'Trade Type', 'Description', 'PnL', 'Balance'])

# Add new entry
if submitted:
    timestamp = pd.to_datetime(f"{date} {trade_time}")
    new_row = pd.DataFrame({
        'Date': [timestamp],
        'Time': [trade_time.strftime("%H:%M:%S")],
        'Trade Type': [trade_type],
        'Description': [description],
        'PnL': [pnl],
        'Balance': [balance]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.sort_values('Date', inplace=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("✅ Trade added successfully!")

# Display dashboard if data exists
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)

    # Sidebar filters
    st.sidebar.header("Filters")
    start_date = st.sidebar.date_input("Start Date", value=df['Date'].min().date())
    end_date = st.sidebar.date_input("End Date", value=df['Date'].max().date())
    trade_type_filter = st.sidebar.multiselect("Trade Type", options=df['Trade Type'].unique().tolist(), default=df['Trade Type'].unique().tolist())

    filtered_df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date)) & (df['Trade Type'].isin(trade_type_filter))]

    if not filtered_df.empty:
        # Summary metrics
        balance = filtered_df['Balance'].iloc[-1]
        monthly_pnl = filtered_df[filtered_df['Date'] >= pd.Timestamp.now() - pd.DateOffset(months=1)]['PnL'].sum()
        yearly_pnl = filtered_df[filtered_df['Date'] >= pd.Timestamp.now() - pd.DateOffset(years=1)]['PnL'].sum()

        # Win rate calculation
        total_trades = len(filtered_df)
        winning_trades = len(filtered_df[filtered_df['PnL'] > 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        # KPI Cards
        with st.container():
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Balance", f"${balance:,.2f}")
            col2.metric("PnL This Month", f"${monthly_pnl:,.2f}")
            col3.metric("PnL This Year", f"${yearly_pnl:,.2f}")
            col4.metric("Win Rate", f"{win_rate:.2f}%")
            col5.metric("Total Trades", f"{total_trades}")

        # PnL Summary Chart as Line Graph
        st.subheader("PnL Over Time")
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(filtered_df['Date'], filtered_df['PnL'].cumsum(), marker='o', linestyle='-', color='teal', label='Cumulative PnL')
        ax.set_ylabel('Cumulative PnL ($)')
        ax.set_xlabel('Date')
        ax.axhline(0, color='black', linewidth=0.8)
        ax.legend()
        st.pyplot(fig)

        # Optional: Show raw data
        with st.expander("📄 Raw Data"):
            st.dataframe(filtered_df)
    else:
        st.warning("⚠️ No data available for the selected filters.")
else:
    st.info("👈 Add your first trade using the form on the left.")
