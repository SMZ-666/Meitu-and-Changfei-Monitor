import requests
import pandas as pd
import re


def get_short_sell_data():

    url = "https://www.hkex.com.hk/eng/stat/smstat/ssturnover/ncms/mshtmain.htm"

    response = requests.get(url)

    response.encoding = "utf-8"

    text = response.text


    report = re.search(
        r"<pre>(.*?)</pre>",
        text,
        re.S
    ).group(1)


    lines = report.split("\n")


    data = []


    for line in lines:

        match = re.match(
            r"\s*(\d+)\s+([A-Z0-9 &\-\']+?)\s+([\d,]+)\s+([\d,]+)",
            line
        )


        if match:

            code = match.group(1)

            name = match.group(2).strip()

            turnover_sh = match.group(3)

            turnover_dollar = match.group(4)


            data.append(
                [
                    code,
                    name,
                    turnover_sh,
                    turnover_dollar
                ]
            )


    df = pd.DataFrame(
        data,
        columns=[
            "Code",
            "Name",
            "Turnover (SH)",
            "Turnover ($)"
        ]
    )


    df["Turnover (SH)"] = (
        df["Turnover (SH)"]
        .str.replace(",", "")
        .astype(float)
    )


    df["Turnover ($)"] = (
        df["Turnover ($)"]
        .str.replace(",", "")
        .astype(float)
    )


    return df

if __name__ == "__main__":

    df = get_short_sell_data()

    print(
        df[
            df["Code"].isin(["1357","6869"])
        ]
    )