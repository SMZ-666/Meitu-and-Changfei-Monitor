import streamlit as st
import pandas as pd
import re

from market_scraper import get_market_turnover
from short_sell_scraper import get_short_sell_data
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

    # ========================
    # Market Data
    # ========================

    market = get_market_turnover(code)

    if market is None:
        st.error(
            "No market turnover data found."
        )
        st.stop()


    total_turnover = float(
        market["Turnover"]
    )


    # ========================
    # Extract Price
    # Works with:
    # HK$4.830
    # HKD4.830
    # ========================

    price_text = str(
        market["Price"]
    )

    price_match = re.search(
        r"(\d+(?:\.\d+)?)",
        price_text
    )

    if price_match is None:
        st.error(
            f"Could not read market price: {price_text}"
        )
        st.stop()

    price = float(
        price_match.group(1)
    )


    # ========================
    # Short Selling Data
    # ========================

    short_df = get_short_sell_data()

    short_row_df = short_df[
        short_df["Code"].astype(str) == str(code)
    ]


    if len(short_row_df) == 0:
        st.error(
            "No short selling data found."
        )
        st.stop()


    short_row = short_row_df.iloc[0]


    short_shares = float(
        short_row["Turnover (SH)"]
    )


    short_turnover = float(
        short_row["Turnover ($)"]
    )


    # ========================
    # Total Shares
    # ========================

    total_shares = (
        total_turnover /
        price
    )


    # ========================
    # Share-based Short Ratio
    # ========================

    if total_shares > 0:

        short_ratio = (
            short_shares /
            total_shares *
            100
        )

    else:

        short_ratio = 0


    short_ratio = round(
        short_ratio,
        2
    )


    # ========================
    # Save History
    # ========================

    history_data = pd.DataFrame(
        {
            "Code": [
                int(code)
            ],

            "Name": [
                market["Name"]
            ],

            "Date": [
                pd.Timestamp.today()
                .strftime("%Y-%m-%d")
            ],

            "Total Shares": [
                int(total_shares)
            ],

            "Short Shares": [
                int(short_shares)
            ],

            "Short Selling Turnover": [
                int(short_turnover)
            ],

            "Short Selling Ratio": [
                short_ratio
            ]
        }
    )


    save_history(
        history_data
    )


    # ========================
    # Display
    # ========================

    st.subheader(
        selected
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "Market Price",
            f"HK${price:.3f}"
        )


    with col2:

        st.metric(
            "Total Shares",
            f"{total_shares:,.0f}"
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
            "Short Selling Shares",
            f"{short_shares:,.0f}"
        )


    with col5:

        st.metric(
            "Short Selling Turnover",
            f"HK${short_turnover / 1e6:.2f}M"
        )


    st.divider()


    # ========================
    # Historical Data
    # ========================

    st.subheader(
        "Historical Short Selling Data"
    )


    try:

        history = pd.read_csv(
            "history.csv"
        )


        stock_history = history[
            history["Code"].astype(str)
            == str(code)
        ].copy()


        stock_history = (
            stock_history
            .sort_values(
                "Date"
            )
        )

        st.dataframe(
            stock_history,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Code": st.column_config.NumberColumn(
                    "Code",
                    format="%d"
                ),

                "Total Shares": st.column_config.NumberColumn(
                    "Total Shares",
                    format="%,d"
                ),

                "Short Shares": st.column_config.NumberColumn(
                    "Short Shares",
                    format="%,d"
                ),

                "Short Selling Turnover": st.column_config.NumberColumn(
                    "Short Selling Turnover",
                    format="HK$%,d"
                ),

                "Short Selling Ratio": st.column_config.NumberColumn(
                    "Short Selling Ratio",
                    format="%.2f%%"
                )
            }
        )


        if len(stock_history) >= 2:

            st.subheader(
                "Short Selling Ratio Trend"
            )


            chart_data = (
                stock_history
                .set_index(
                    "Date"
                )
                [
                    "Short Selling Ratio"
                ]
            )


            st.line_chart(
                chart_data
            )


        else:

            st.info(
                "More historical data points are needed before a trend chart can be displayed."
            )


    except FileNotFoundError:

        st.info(
            "No historical data available yet."
        )