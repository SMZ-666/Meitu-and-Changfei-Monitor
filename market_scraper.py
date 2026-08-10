from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import time


def create_driver():

    options = Options()

    # Streamlit Cloud settings
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Cloud Chromium location
    options.binary_location = "/usr/bin/chromium"


    driver = webdriver.Chrome(
        service=Service(
            "/usr/bin/chromedriver"
        ),
        options=options
    )

    return driver



def convert_turnover(value):

    value = value.replace(",", "").strip()


    if value.endswith("B"):

        return float(value[:-1]) * 1_000_000_000


    elif value.endswith("M"):

        return float(value[:-1]) * 1_000_000


    elif value.endswith("K"):

        return float(value[:-1]) * 1_000


    else:

        return float(value)



def get_market_turnover(stock_code):

    stock_code = str(stock_code)


    url = (
        "https://www.hkex.com.hk/"
        "Market-Data/Securities-Prices/Equities"
        "?sc_lang=en"
    )


    driver = create_driver()


    try:

        driver.get(url)

        time.sleep(8)



        # -------------------------
        # Find visible search box
        # -------------------------

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

            raise Exception(
                "HKEX search box not found"
            )



        # -------------------------
        # Enter stock code
        # Using JS because HKEX
        # blocks normal send_keys
        # -------------------------

        driver.execute_script(
            """
            arguments[0].value = arguments[1];

            arguments[0].dispatchEvent(
                new Event(
                    'input',
                    {bubbles:true}
                )
            );

            arguments[0].dispatchEvent(
                new Event(
                    'change',
                    {bubbles:true}
                )
            );
            """,
            search_box,
            stock_code
        )


        time.sleep(2)



        # -------------------------
        # Click apply filter
        # -------------------------

        buttons = driver.find_elements(
            By.CLASS_NAME,
            "etps_apply_btn"
        )


        apply_button = None


        for button in buttons:

            if button.is_displayed():

                apply_button = button
                break



        if apply_button is None:

            raise Exception(
                "Apply button not found"
            )



        driver.execute_script(
            "arguments[0].click();",
            apply_button
        )


        time.sleep(8)



        # -------------------------
        # Find stock row
        # -------------------------

        rows = driver.find_elements(
            By.CSS_SELECTOR,
            "table.table_equities tr.datarow"
        )


        for row in rows:


            cells = row.find_elements(
                By.TAG_NAME,
                "td"
            )


            if len(cells) >= 4:


                code = cells[0].text.strip()


                if code == stock_code:


                    return {

                        "Code": code,

                        "Name":
                        cells[1].text.strip(),

                        "Price":
                        cells[2]
                        .text
                        .replace(
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



# -------------------------
# Local test
# -------------------------

if __name__ == "__main__":


    print("MEITU:")

    print(
        get_market_turnover(
            "1357"
        )
    )


    print()


    print("YOFC:")

    print(
        get_market_turnover(
            "6869"
        )
    )