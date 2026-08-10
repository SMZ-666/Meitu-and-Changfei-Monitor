from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time


def create_driver():
    options = Options()

    # Let Selenium Manager provision a compatible Chrome
    # and ChromeDriver automatically.
    options.browser_version = "stable"

    # Required/recommended for headless cloud environments
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")

    # IMPORTANT:
    # Do not specify Service(...)
    # Do not specify chromedriver path
    # Do not specify Chrome binary path
    #
    # Selenium Manager handles them.
    driver = webdriver.Chrome(options=options)

    return driver


def convert_turnover(value):
    value = str(value).replace(",", "").strip()

    if value.endswith("B"):
        return float(value[:-1]) * 1_000_000_000

    if value.endswith("M"):
        return float(value[:-1]) * 1_000_000

    if value.endswith("K"):
        return float(value[:-1]) * 1_000

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
        # ---------------------------------
        # 1. Open HKEX Equities page
        # ---------------------------------

        driver.get(url)

        wait = WebDriverWait(driver, 30)

        # Wait until HKEX's JS creates the stock table rows
        wait.until(
            lambda d: len(
                d.find_elements(
                    By.CSS_SELECTOR,
                    "table.table_equities tr.datarow"
                )
            ) > 0
        )

        # ---------------------------------
        # 2. Find the visible stock search
        # ---------------------------------

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
            raise RuntimeError(
                "HKEX stock search box could not be found."
            )

        # ---------------------------------
        # 3. Enter code using JavaScript
        #
        # HKEX has hidden/duplicate elements,
        # so normal send_keys() was unreliable.
        # ---------------------------------

        driver.execute_script(
            """
            arguments[0].value = arguments[1];

            arguments[0].dispatchEvent(
                new Event(
                    'input',
                    {bubbles: true}
                )
            );

            arguments[0].dispatchEvent(
                new Event(
                    'change',
                    {bubbles: true}
                )
            );
            """,
            search_box,
            stock_code
        )

        time.sleep(1)

        # ---------------------------------
        # 4. Find visible APPLY FILTERS
        # ---------------------------------

        apply_buttons = driver.find_elements(
            By.CLASS_NAME,
            "etps_apply_btn"
        )

        apply_button = None

        for button in apply_buttons:
            if button.is_displayed():
                apply_button = button
                break

        if apply_button is None:
            raise RuntimeError(
                "HKEX APPLY FILTERS button could not be found."
            )

        driver.execute_script(
            "arguments[0].click();",
            apply_button
        )

        # ---------------------------------
        # 5. Wait specifically for our stock
        # ---------------------------------

        def find_target_row(d):
            rows = d.find_elements(
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

        target_row = wait.until(
            find_target_row
        )

        # ---------------------------------
        # 6. Extract values
        # ---------------------------------

        cells = target_row.find_elements(
            By.TAG_NAME,
            "td"
        )

        code = cells[0].text.strip()
        name = cells[1].text.strip()

        price = (
            cells[2]
            .text
            .strip()
            .replace("\n", " ")
        )

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


# ---------------------------------
# Local test
# ---------------------------------

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