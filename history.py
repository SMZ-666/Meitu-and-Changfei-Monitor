import pandas as pd
import os
from datetime import datetime


def save_history(data):

    file = "history.csv"

    if "Date" not in data.columns:

        data["Date"] = datetime.today().strftime(
            "%Y-%m-%d"
        )


    if os.path.exists(file):

        old_data = pd.read_csv(file)

        combined = pd.concat(
            [
                old_data,
                data
            ],
            ignore_index=True
        )

    else:

        combined = data


    combined = combined.drop_duplicates(
        subset=[
            "Code",
            "Date"
        ],
        keep="last"
    )


    combined.to_csv(
        file,
        index=False
    )