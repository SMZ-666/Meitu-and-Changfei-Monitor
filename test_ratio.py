from market_scraper import get_market_turnover
from short_sell_scraper import get_short_sell_data


stocks = {
    "1357": "MEITU",
    "6869": "YOFC"
}


# Get short selling data once
short_df = get_short_sell_data()


for code, name in stocks.items():

    print("\n==========================")
    print(name, code)
    print("==========================")


    # -----------------------
    # Normal turnover
    # -----------------------

    market_data = get_market_turnover(code)

    total_turnover = market_data["Turnover"]


    print(
        "Total Turnover:",
        f"{total_turnover:,.0f}",
        "HKD"
    )


    # -----------------------
    # Short selling turnover
    # -----------------------

    short_row = short_df[
        short_df["Code"] == code
    ]


    if len(short_row) == 0:

        print(
            "No short selling data"
        )

        continue


    short_turnover = float(
        short_row["Turnover ($)"].iloc[0]
    )


    print(
        "Short Selling Turnover:",
        f"{short_turnover:,.0f}",
        "HKD"
    )


    # -----------------------
    # Ratio
    # -----------------------

    ratio = (
        short_turnover /
        total_turnover
        *
        100
    )


    print(
        "Short Selling Ratio:",
        round(ratio,2),
        "%"
    )