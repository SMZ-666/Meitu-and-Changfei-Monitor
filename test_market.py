import requests
from bs4 import BeautifulSoup


url = "https://www.hkex.com.hk/Market-Data/Securities-Prices/Equities?sc_lang=en"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print(response.status_code)

print("6869" in response.text)
print("YOFC" in response.text)

print(response.text[:500])