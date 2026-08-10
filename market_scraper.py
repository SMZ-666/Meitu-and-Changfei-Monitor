from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from webdriver_manager.chrome import ChromeDriverManager

import shutil
import time


def convert_turnover(value):

    value = str(value).replace(",", "").strip()

    if value.endswith("B"):
        return float(value[:-1]) * 1_000_000_000

    elif value.endswith("M"):
        return float(value[:-1]) * 1_000_000

    elif value.endswith("K"):
        return float(value[:-1]) * 1_000

    else:
        return float(value)


def create_driver():

    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # --------------------------------
    # Find Chrome / Chromium
    # Works on Mac and Streamlit Linux
    # --------------------------------

    possible_browsers = [
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    ]

    for browser in possible_browsers:

        if browser:

            options.binary_location = browser
            break

    # --------------------------------
    # Use installed chromedriver first
    # Otherwise webdriver-manager
    # --------------------------------

    system_driver = shutil.which("chromedriver")

    if system_driver:

        driver = webdriver.Chrome(
            service=Service(system_driver),
            options=options
        )

    else:

        driver = webdriver.Chrome(
            service=Service(
                ChromeDriverManager().install()
            ),
            options=options
        )

    return driver


def get_market_turnover(stock_code):

    stock_code = str(stock_code)

    url = (
        "https://www.hkex.com.hk/"
        "Market-Data/Securities-Prices/Equities"
        "?sc_lang=en"
    )

    driver = create_driver()

    try:

        # ============================
        # Open HKEX
        # ============================

        driver.get(url)

        time.sleep(8)


        # ============================
        # Find VISIBLE search box
        # ============================

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
                "Visible HKEX stock search box was not found."
            )


        # ============================
        # Insert stock code with JS
        # Avoid send_keys()
        # ============================

        driver.execute_script(
            """
            arguments[0].value = arguments[1];

            arguments[0].dispatchEvent(
                new Event('input', {
                    bubbles: true
                })
            );

            arguments[0].dispatchEvent(
                new Event('change', {
                    bubbles: true
                })
            );
            """,
            search_box,
            stock_code
        )

        time.sleep(2)


        # ============================
        # Find VISIBLE Apply button
        # ============================

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
                "Visible APPLY FILTERS button was not found."
            )


        # ============================
        # Click using JavaScript
        # ============================

        driver.execute_script(
            "arguments[0].click();",
            apply_button
        )


        # ============================
        # Wait until requested stock
        # appears in table
        # ============================

        wait = WebDriverWait(
            driver,
            20
        )


        def stock_row_loaded(driver):

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

                        return row

            return False


        row = wait.until(
            stock_row_loaded
        )


        # ============================
        # Extract row
        # ============================

        cells = row.find_elements(
            By.TAG_NAME,
            "td"
        )


        code = cells[0].text.strip()

        name = cells[1].text.strip()

        price = cells[2].text.strip()

        turnover_text = cells[3].text.strip()


        turnover = convert_turnover(
            turnover_text
        )


        return {
            "Code": code,
            "Name": name,
            "Price": price,
            "Turnover": turnover
        }


    finally:

        driver.quit()


# ==================================
# Test
# ==================================

if __name__ == "__main__":

    print("MEITU:")
    print(
        get_market_turnover("1357")
    )

    print()

    print("YOFC:")
    print(
        get_market_turnover("6869")
    )