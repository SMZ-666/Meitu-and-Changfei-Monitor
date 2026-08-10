import streamlit as st
import pandas as pd
from datetime import date

from hkex_scraper import get_short_sell_data
from market_scraper import get_market_turnover
from history import save_history


stocks = {
    "Meitu (1357)": "1357",
    "YOFC (6869)": "6869"
}


st.title("HK Stock Short Selling Monitor")


selected = st.selectbox(
    "Select Stock",
    list(stocks.keys())
)

code = stocks[selected]


if st.button("Get Data"):

    # ==========================
    # Short selling data
    # ==========================

    short_df = get_short_sell_data()

    short_row_df = short_df[
        short_df["Code"] == code
    ]

    if len(short_row_df) == 0:

        st.error("No short selling data found.")

        st.stop()

    short_row = short_row_df.iloc[0]

    short_turnover = float(
        short_row["Turnover ($)"]
    )

    short_turnover_sh = int(
        short_row["Turnover (SH)"]
    )

    short_price = float(
        short_row["Price"]
    )

    stock_name = short_row["Name"]


    # ==========================
    # Market data
    # ==========================

    market = get_market_turnover(code)

    if market is None:

        st.error("No market turnover data found.")

        st.stop()

    total_turnover = float(
        market["Turnover"]
    )

    market_price_full = market["Price"]

    market_price = str(
        market_price_full
    ).split()[0]


    # ==========================
    # Short selling ratio
    # ==========================

    if total_turnover > 0:

        short_ratio = (
            short_turnover /
            total_turnover *
            100
        )

    else:

        short_ratio = 0


    # ==========================
    # Save historical data
    # ==========================

    history_data = pd.DataFrame(
        [
            {
                "Code": code,
                "Name": stock_name,
                "Turnover (SH)": short_turnover_sh,
                "Turnover ($)": int(short_turnover),
                "Price": short_price,
                "Date": str(date.today())
            }
        ]
    )

    save_history(
        history_data
    )


    # ==========================
    # Current data display
    # ==========================

    st.subheader(
        selected

    )
    st.caption(
        f"Data Date: {date.today()}"
    )

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Market Price",
            market_price
        )


    with col2:

        if total_turnover >= 1_000_000_000:

            turnover_display = (
                f"HK${total_turnover / 1_000_000_000:.2f}B"
            )

        else:

            turnover_display = (
                f"HK${total_turnover / 1_000_000:.2f}M"
            )

        st.metric(
            "Total Turnover",
            turnover_display
        )


    with col3:

        st.metric(
            "Short Selling Ratio",
            f"{short_ratio:.2f}%"
        )


    st.divider()


    col4, col5 = st.columns(2)


    with col4:

        st.metric(
            "Short Selling Turnover",
            f"HK${short_turnover / 1_000_000:.2f}M"
        )


    with col5:

        st.metric(
            "Short Selling Price",
            f"HK${short_price:.2f}"
        )


    # ==========================
    # Historical section
    # ==========================

    st.subheader(
        "Historical Short Selling Data"
    )


    history = pd.read_csv(
        "history.csv"
    )


    stock_history = history[
        history["Code"].astype(str) == code
    ].copy()


    stock_history = stock_history.drop_duplicates(
        subset=[
            "Code",
            "Name",
            "Turnover (SH)",
            "Turnover ($)",
            "Price",
            "Date"
        ]
    )


    stock_history = stock_history.sort_values(
        "Date"
    )


    st.dataframe(
        stock_history.reset_index(drop=True),
        hide_index=True,
        use_container_width=True
    )


    # ==========================
    # Historical turnover chart
    # ==========================

    if len(stock_history) > 1:

        chart_data = stock_history[
            [
                "Date",
                "Turnover ($)"
            ]
        ].copy()

        chart_data["Date"] = pd.to_datetime(
            chart_data["Date"]
        )

        chart_data = chart_data.set_index(
            "Date"
        )

        st.line_chart(
            chart_data
        )

    else:

        st.info(
            "More historical data points are needed before a trend chart can be displayed."
        )