import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, time
import os

# File to store trades
RESET_TRIGGER = "Reset Metrics"
DATA_FILE = "trades.csv"

# Reset logic
if 'confirm_reset_shown' not in st.session_state:
    st.session_state.confirm_reset_shown = False

st.sidebar.markdown(
    "<a href='https://example.com' target='_blank'><button style='width: 100%'>🌐 Visit Website</button></a>",
    unsafe_allow_html=True
)
if st.sidebar.button("🔁 Reset All Trades"):
    st.session_state.confirm_reset_shown = True

if st.session_state.confirm_reset_shown:
    confirm = st.sidebar.checkbox("Confirm reset?")
    if confirm and st.sidebar.button("✅ Confirm Delete"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.rerun()

# Title
st.title("📈 Trading Performance Dashboard")

# Load or create CSV
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=['Date'])
    df['Trade Type'].fillna('Unknown', inplace=True)
else:
    df = pd.DataFrame(columns=['Date', 'Time', 'Trade Type', 'Description', 'PnL', 'Balance'])

# Display dashboard if data exists
if not df.empty:
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)

    # Sidebar filters
    with st.sidebar.expander("🧰 Filters", expanded=True):
        start_date = st.date_input("Start Date", value=df['Date'].min().date())
        end_date = st.date_input("End Date", value=df['Date'].max().date())
        trade_type_options = df['Trade Type'].dropna().unique().tolist()
        trade_type_filter = st.multiselect(
            "Trade Type",
            options=trade_type_options,
            default=trade_type_options
        )

    filtered_df = df[
        (df['Date'] >= pd.to_datetime(start_date)) &
        (df['Date'] <= pd.to_datetime(end_date)) &
        (df['Trade Type'].isin(trade_type_filter))
    ]

    if not filtered_df.empty:
        # Summary metrics
        balance = filtered_df['Balance'].iloc[-1]
        monthly_pnl = filtered_df[filtered_df['Date'] >= pd.Timestamp.now() - pd.DateOffset(months=1)]['PnL'].sum()
        yearly_pnl = filtered_df[filtered_df['Date'] >= pd.Timestamp.now() - pd.DateOffset(years=1)]['PnL'].sum()

        # Win rate calculation
        total_trades = len(filtered_df)
        winning_trades = len(filtered_df[filtered_df['PnL'] > 0])
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

        # KPI Cards in two rows
        col1, col2, col3 = st.columns(3)
        col1.metric("Balance", f"${balance:,.2f}")
        col2.metric("PnL This Month", f"${monthly_pnl:,.2f}")
        col3.metric("PnL This Year", f"${yearly_pnl:,.2f}")

        col4, col5 = st.columns(2)
        col4.metric("Win Rate", f"{win_rate:.2f}%")
        col5.metric("Total Trades", f"{total_trades}")

        # PnL Summary Chart as Line Graph
        with st.container():
            st.subheader("PnL Over Time")
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.plot(filtered_df['Date'], filtered_df['PnL'].cumsum(), marker='o', linestyle='-', color='teal', label='Cumulative PnL')
            ax.set_ylabel('Cumulative PnL ($)')
            ax.set_xlabel('Date')
            ax.axhline(0, color='black', linewidth=0.8)
            ax.legend()
            st.pyplot(fig)

    # Raw data view
    with st.container():
        st.subheader("📄 Raw Data")
        st.dataframe(filtered_df.reset_index(drop=True).rename(lambda x: x + 1))

# Trade Entry Section
with st.container():
    st.subheader("➕ Add New Trade Entry")

with st.form("trade_form"):
    date = st.date_input("Date", value=datetime.today())
    trade_time = st.time_input("Time", value=datetime.now().time())
    trade_type = st.selectbox("Trade Type", ["Long", "Short"])
    description = st.text_input("Description")
    pnl = st.number_input("PnL ($)", step=0.01, format="%.2f")
    submitted = st.form_submit_button("Add Trade")

if submitted:
    timestamp = pd.to_datetime(f"{date} {trade_time}")
    new_row = pd.DataFrame({
        'Date': [timestamp],
        'Time': [trade_time.strftime("%H:%M:%S")],
        'Trade Type': [trade_type],
        'Description': [description],
        'PnL': [pnl],
        'Balance': [df['Balance'].iloc[-1] + pnl if not df.empty else pnl]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.sort_values('Date', inplace=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("✅ Trade added successfully!")
else:
    st.info("👈 Add your first trade using the form above.")
