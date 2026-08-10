from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import time


def create_driver():

    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.browser_version = "stable"

    driver = webdriver.Chrome(
        options=options
    )

    return driver



def convert_turnover(value):

    value = value.replace(",", "").strip()

    if value.endswith("B"):
        return float(value[:-1]) * 1_000_000_000

    if value.endswith("M"):
        return float(value[:-1]) * 1_000_000

    if value.endswith("K"):
        return float(value[:-1]) * 1_000

    return float(value)



def get_market_turnover(stock_code):

    driver = create_driver()


    try:

        driver.get(
            "https://www.hkex.com.hk/"
            "Market-Data/Securities-Prices/Equities"
            "?sc_lang=en"
        )


        # wait for page scripts
        time.sleep(10)


        # find search box

        search_boxes = driver.find_elements(
            By.ID,
            "tags"
        )

        search_box = None

        for box in search_boxes:

            if box.is_displayed():

                search_box = box
                break


        if search_box is None:
            raise Exception(
                "Search box not found"
            )


        # use javascript input

        driver.execute_script(
            """
            arguments[0].value = arguments[1];

            arguments[0].dispatchEvent(
                new Event('input',
                {bubbles:true})
            );
            """,
            search_box,
            str(stock_code)
        )


        time.sleep(2)


        # click apply

        buttons = driver.find_elements(
            By.CLASS_NAME,
            "etps_apply_btn"
        )


        for button in buttons:

            if button.is_displayed():

                driver.execute_script(
                    "arguments[0].click();",
                    button
                )

                break


        # IMPORTANT
        # wait after filtering

        time.sleep(10)



        rows = driver.find_elements(
            By.CSS_SELECTOR,
            "tr.datarow"
        )


        for row in rows:

            cells = row.find_elements(
                By.TAG_NAME,
                "td"
            )


            if len(cells) >= 4:

                code = cells[0].text.strip()


                if code == str(stock_code):

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



if __name__ == "__main__":

    print("MEITU:")
    print(get_market_turnover("1357"))

    print()

    print("YOFC:")
    print(get_market_turnover("6869"))