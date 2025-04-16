from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import os
import undetected_chromedriver as uc

THREADS_COOKIE = "ds_user_id=73803533548; sessionid=73803533548%3ARuiWN6Im6053Ai%3A23%3AAYfC9yG70LSVHtc3xA_Qx9gXwN7uc5YvMj3RVjYPeQ; csrftoken=53dtYsAQK1jVLIAakTGNXubEGQg9ueCZ;"
COMMENT_TEXT = "我也是患者，歡迎加入異膚社群和大家一起交流！！~\nhttps://line.me/ti/g2/oSdVRcm28E5iu4DfFsOCvTzp6fTPOBXLa3SB9w"

SEARCH_URL = "https://www.threads.net/search?q=異位性皮膚炎"

if os.path.exists("commented.json"):
    with open("commented.json", "r") as f:
        commented_posts = set(json.load(f))
else:
    commented_posts = set()

def auto_comment():
    total_posts = 0
    commented_count = 0

    print("🚀 啟動 undetected Chrome 瀏覽器")
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")

    driver = uc.Chrome(options=options)

    # 加入 cookie
    driver.get("https://www.threads.net")
    time.sleep(5)
    for pair in THREADS_COOKIE.split(";"):
        if "=" in pair:
            name, value = pair.strip().split("=", 1)
            driver.add_cookie({
                "name": name.strip(),
                "value": value.strip(),
                "domain": ".threads.net",
                "path": "/"
            })

    print("🌐 前往搜尋頁")
    driver.get(SEARCH_URL)
    time.sleep(5)

    # 模擬滑動加載更多
    for _ in range(5):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)

    print("🔍 解析頁面貼文")
    articles = driver.find_elements(By.TAG_NAME, "article")
    total_posts = len(articles)
    print(f"✅ 共抓到 {total_posts} 則貼文")

    for article in articles:
        try:
            href = article.find_element(By.CSS_SELECTOR, 'a[href*="/@"]').get_attribute("href")
            if not href or href in commented_posts:
                continue

            print(f"📌 開啟貼文：{href}")
            driver.execute_script("window.open(arguments[0]);", href)
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(5)

            content = driver.find_element(By.TAG_NAME, "article").text
            if "異位性皮膚炎" in content:
                print("🟢 發現關鍵字，嘗試留言...")
                textarea = driver.find_element(By.TAG_NAME, "textarea")
                textarea.send_keys(COMMENT_TEXT)
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                print("✅ 留言成功！")
                commented_count += 1
                commented_posts.add(href)
                with open("commented.json", "w") as f:
                    json.dump(list(commented_posts), f)
            else:
                print("⏭ 無關鍵字，略過")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 貼文處理失敗：{e}")
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    driver.quit()
    print(f"📊 掃描 {total_posts} 篇，留言成功 {commented_count} 篇")
    return total_posts, commented_count
