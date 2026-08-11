import streamlit as st
import pandas as pd

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


    total_turnover = market["Turnover"]



    # ========================
    # Extract Price
    # ========================

    price = float(
        market["Price"]
        .split()[0]
        .replace(
            "HK$",
            ""
        )
    )



    # ========================
    # Short Selling Data
    # ========================

    short_df = get_short_sell_data()


    short_row = short_df[
        short_df["Code"] == code
    ]



    if len(short_row) > 0:


        short_shares = float(
            short_row["Turnover (SH)"]
            .iloc[0]
        )


        short_turnover = float(
            short_row["Turnover ($)"]
            .iloc[0]
        )


    else:

        short_shares = 0

        short_turnover = 0



    # ========================
    # Share-based Short Ratio
    # ========================

    total_shares = (
        total_turnover /
        price
    )


    short_ratio = (
        short_shares /
        total_shares *
        100
    )


    short_ratio = round(
        short_ratio,
        2
    )



    # ========================
    # Save History
    # ========================

    if len(short_row) > 0:
        history_data = pd.DataFrame(
            {
                "Code": [int(code)],

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
    # Main Display
    # ========================


    st.subheader(
        selected
    )


    col1, col2, col3 = st.columns(3)



    with col1:

        st.metric(
            "Market Price",
            market["Price"]
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
            history["Code"] == int(code)
        ]


        stock_history = (
            stock_history
            .sort_values(
                "Date"
            )
        )


        st.dataframe(
            stock_history,
            hide_index=True
        )



        if len(stock_history) >= 2:


            st.subheader(
                "Short Selling Ratio Trend"
            )


            chart_data = (
                stock_history
                .set_index("Date")
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