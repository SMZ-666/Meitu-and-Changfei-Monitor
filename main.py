from hkex_scraper import get_short_sell_data


df = get_short_sell_data()


print(df.head())


print(
    df[
        df["Code"].isin(["1357","6869"])
    ]
)