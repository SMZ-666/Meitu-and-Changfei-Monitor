import streamlit as st
import pandas as pd
import datetime

from hkex_scraper import get_short_sell_data
from history import save_history


# Page title
st.title("HKEX Short Selling Monitor")

st.write(
    "Monitor short selling turnover for selected HK stocks."
)


# Stock selection
stock = st.selectbox(
    "Select Stock",
    [
        "Meitu (1357)",
        "YOFC (6869)"
    ]
)


# Button
if st.button("Get Data"):

    # Get HKEX data
    df = get_short_sell_data()


    # Select stock code
    if stock == "Meitu (1357)":
        code = "1357"
    else:
        code = "6869"


    # Filter selected stock
    result = df[
        df["Code"] == code
    ].copy()


    if result.empty:

        st.error("No data found.")

    else:

        # Add date
        result["Date"] = str(datetime.date.today())


        # Save into history.csv
        save_history(result)


        # Extract values
        row = result.iloc[0]


        st.subheader(stock)


        # Display metrics
        col1, col2, col3 = st.columns(3)


        col1.metric(
            "Price (HKD)",
            f"${row['Price']}"
        )


        col2.metric(
            "Turnover (SH)",
            f"{row['Turnover (SH)']:,}"
        )


        col3.metric(
            "Turnover ($)",
            f"HK${row['Turnover ($)']:,}"
        )


        st.divider()


        # Current data table
        st.subheader("Latest Data")

        st.dataframe(
            result,
            hide_index=True
        )


        # Historical chart
        st.divider()

        st.subheader(
            "Historical Short Selling Turnover"
        )


        history = pd.read_csv(
            "history.csv"
        )


        stock_history = history[
            history["Code"] == code
        ]


        stock_history = stock_history.sort_values(
            "Date"
        )


        st.line_chart(
            stock_history.set_index("Date")["Turnover ($)"]
        )