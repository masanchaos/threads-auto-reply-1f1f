import subprocess
subprocess.run(["playwright", "install", "--with-deps"])
from playwright.sync_api import sync_playwright
import time
import json
import os

THREADS_COOKIE = "ds_user_id=73803533548;sessionid=73803533548%3ARuiWN6Im6053Ai%3A23%3AAYejYhkcrIxZX1sxQNDVtbVs8ZJmMVpjESncWAfJbw; csrftoken=53dtYsAQK1jVLIAakTGNXubEGQg9ueCZ;"  # ← 請自己填入

COMMENT_TEXT = '''我也是患者，歡迎加入異膚社群和大家一起交流！！~
https://line.me/ti/g2/oSdVRcm28E5iu4DfFsOCvTzp6fTPOBXLa3SB9w?utm_source=invitation&utm_medium=link_copy&utm_campaign=default'''

SEARCH_URL = "https://www.threads.net/search?q=異位性皮膚炎"

if os.path.exists("commented.json"):
    with open("commented.json", "r") as f:
        commented_posts = set(json.load(f))
else:
    commented_posts = set()

def auto_comment():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context()
        context.add_cookies([{
            'name': pair.split('=')[0].strip(),
            'value': pair.split('=')[1].strip(),
            'domain': '.threads.net',
            'path': '/',
            'httpOnly': False,
            'secure': True
        } for pair in THREADS_COOKIE.split(';') if '=' in pair])

        page = context.new_page()
        page.goto(SEARCH_URL)
        time.sleep(3)
        for _ in range(5):
            page.mouse.wheel(0, 1500)
            time.sleep(2)

        post_links = page.locator('a[href*="/@"]').all()
        print(f"共找到 {len(post_links)} 則貼文")

        for link in post_links:
            href = link.get_attribute("href")
            if not href or href in commented_posts:
                continue

            post_url = f"https://www.threads.net{href}"
            print(f"🔍 檢查貼文：{post_url}")

            post_page = context.new_page()
            post_page.goto(post_url)
            time.sleep(3)

            try:
                content = post_page.locator("article").inner_text()
                if "異位性皮膚炎" in content:
                    print("✅ 發現關鍵字，開始留言...")
                    comment_box = post_page.locator("textarea").first
                    comment_box.fill(COMMENT_TEXT)
                    comment_box.press("Enter")
                    print("📝 留言完成")
                    commented_posts.add(href)
                    with open("commented.json", "w") as f:
                        json.dump(list(commented_posts), f)
                else:
                    print("❌ 沒有關鍵字，跳過")
            except Exception as e:
                print("⚠️ 發生錯誤：", e)

            post_page.close()
            time.sleep(4)

        browser.close()

if __name__ == "__main__":
    auto_comment()
