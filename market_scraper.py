from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from io import StringIO
import time


def convert_turnover(value):

    value = str(value).replace(",", "").strip()

    if "B" in value:
        return float(value.replace("B", "")) * 1_000_000_000

    elif "M" in value:
        return float(value.replace("M", "")) * 1_000_000

    elif "K" in value:
        return float(value.replace("K", "")) * 1_000

    else:
        return float(value)



def get_market_turnover(stock_code):

    url = (
        "https://www.hkex.com.hk/"
        "Market-Data/Securities-Prices/Equities?sc_lang=en"
    )

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        options=options
    )

    driver.get(url)

    time.sleep(5)


    # find visible search box
    boxes = driver.find_elements(
        By.ID,
        "tags"
    )

    search_box = None

    for box in boxes:
        if box.is_displayed():
            search_box = box
            break


    if search_box is None:
        driver.quit()
        raise Exception("Search box not found")


    # input stock code
    driver.execute_script(
        """
        arguments[0].value = arguments[1];

        arguments[0].dispatchEvent(
            new Event('input', {bubbles:true})
        );

        arguments[0].dispatchEvent(
            new Event('change', {bubbles:true})
        );
        """,
        search_box,
        stock_code
    )


    time.sleep(2)


    # click apply filter
    button = driver.find_element(
        By.CLASS_NAME,
        "etps_apply_btn"
    )

    driver.execute_script(
        "arguments[0].click();",
        button
    )


    time.sleep(5)


    # ONLY extract the equity table
    table = driver.find_element(
        By.CLASS_NAME,
        "table_equities"
    )

    html = table.get_attribute(
        "outerHTML"
    )


    driver.quit()


    df = pd.read_html(
        StringIO(html)
    )[0]


    # remove duplicated header rows
    df = df[
        df.iloc[:,0]
        .astype(str)
        .str.isnumeric()
    ]


    # set columns
    df.columns = [
        "Code",
        "Name",
        "Price",
        "Turnover",
        "Market Cap",
        "PE",
        "Dividend Yield",
        "Intraday"
    ]


    result = df[
        df["Code"]
        .astype(str)
        == str(stock_code)
    ]


    if len(result) == 0:
        return None


    row = result.iloc[0]


    return {
        "Code": stock_code,
        "Name": row["Name"],
        "Price": row["Price"],
        "Turnover": convert_turnover(row["Turnover"])
    }



if __name__ == "__main__":

    print(get_market_turnover("1357"))

    print(get_market_turnover("6869"))