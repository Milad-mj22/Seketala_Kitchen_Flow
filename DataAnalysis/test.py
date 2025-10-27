from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# ========== تنظیمات مرورگر ==========
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # باز شدن تمام صفحه
# chrome_options.add_argument("--headless")  # اگر نمی‌خواهی مرورگر باز شود، این خط را فعال کن

driver = webdriver.Chrome(options=chrome_options)

# ========== باز کردن سایت ==========
url = "https://www.tgju.org/profile/price_dollar_rl/history"
driver.get(url)
time.sleep(5)  # صبر برای لود کامل داده‌ها

all_data = []

# تابع برای استخراج داده از جدول
def extract_table_data():
    rows = driver.find_elements(By.CSS_SELECTOR, "table.data-table tbody tr")
    page_data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 3:
            date = cols[0].text.strip()
            price = cols[1].text.strip().replace(",", "")
            change = cols[2].text.strip()
            page_data.append({
                "تاریخ": date,
                "قیمت (ریال)": price,
                "تغییر": change
            })
    return page_data


# ========== پیمایش صفحات ==========
for page_num in range(1, 3):  # از صفحه 1 تا 20
    print(f"📄 در حال خواندن صفحه {page_num} ...")
    time.sleep(2)
    
    # استخراج داده‌های جدول فعلی
    all_data.extend(extract_table_data())
    
    # پیدا کردن دکمه صفحه بعد
    try:
        next_btn = driver.find_element(By.XPATH, "/html/body/main/div[1]/div[2]/div[2]/div[1]/div/div[3]/div/div[2]/div/div[1]/a[2]")
        driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
        time.sleep(3)
        next_btn.click()
    except Exception as e:
        print(f"❌ دکمه صفحه {page_num + 1} پیدا نشد یا دیگر صفحه‌ای وجود ندارد.")
        break

# بستن مرورگر
driver.quit()

# ========== ذخیره در اکسل ==========
df = pd.DataFrame(all_data)
df.to_excel("dollar_tgju_selenium.xlsx", index=False)
print("✅ داده‌ها با موفقیت در فایل dollar_tgju_selenium.xlsx ذخیره شدند.")
