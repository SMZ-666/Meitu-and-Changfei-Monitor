import pandas as pd
import os


def save_history(data):

    file = "history.csv"


    if os.path.exists(file):

        old_data = pd.read_csv(file)

        combined = pd.concat(
            [old_data, data],
            ignore_index=True
        )

    else:

        combined = data


    combined.to_csv(
        file,
        index=False
    )