import pandas as pd
import requests


def get_market_turnover():

    url = "https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities?sc_lang=en"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

    tables = pd.read_html(response.text)

    print(len(tables))

    for i, table in enumerate(tables):
        print("\nTABLE", i)
        print(table.head())



get_market_turnover()