from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

import time


def create_driver():

    options = Options()

    # Streamlit Cloud needs headless mode
    options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")

    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--disable-gpu")

    options.add_argument("--window-size=1920,1080")


    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    return driver



def convert_turnover(value):

    value = value.replace(",", "")

    if value.endswith("B"):

        return float(value[:-1]) * 1_000_000_000


    if value.endswith("M"):

        return float(value[:-1]) * 1_000_000


    if value.endswith("K"):

        return float(value[:-1]) * 1_000


    return float(value)



def get_market_turnover(stock_code):


    url = (
        "https://www.hkex.com.hk/"
        "Market-Data/Securities-Prices/Equities"
        "?sc_lang=en"
    )


    driver = create_driver()


    try:

        driver.get(url)

        time.sleep(8)


        boxes = driver.find_elements(
            "id",
            "tags"
        )


        search_box = None


        for box in boxes:

            if box.is_displayed():

                search_box = box

                break



        if search_box is None:

            raise Exception(
                "Search box not found"
            )


        driver.execute_script(
            """
            arguments[0].value = arguments[1];

            arguments[0].dispatchEvent(
                new Event('input',
                {bubbles:true})
            );
            """,
            search_box,
            stock_code
        )


        time.sleep(2)



        buttons = driver.find_elements(
            "class name",
            "etps_apply_btn"
        )


        apply_button = None


        for button in buttons:

            if button.is_displayed():

                apply_button = button

                break



        driver.execute_script(
            "arguments[0].click();",
            apply_button
        )


        time.sleep(8)



        rows = driver.find_elements(
            "css selector",
            "table.table_equities tr.datarow"
        )



        for row in rows:


            cells = row.find_elements(
                "tag name",
                "td"
            )


            if cells[0].text.strip() == stock_code:


                return {

                    "Code":
                    cells[0].text.strip(),

                    "Name":
                    cells[1].text.strip(),

                    "Price":
                    cells[2].text.replace(
                        "\n",
                        " "
                    ),

                    "Turnover":
                    convert_turnover(
                        cells[3].text.strip()
                    )
                }


        return None


    finally:

        driver.quit()