from playwright.sync_api import sync_playwright
import time
import json
import os

# 👉 請貼上你自己的 Cookie（記得保留雙引號）
THREADS_COOKIE = "ds_user_id=73803533548 ; sessionid=73803533548%3ARuiWN6Im6053Ai%3A23%3AAYej861GdeSieOso_E3U5cVX3crXM36516j4cKfOgQ ; csrftoken=53dtYsAQK1jVLIAakTGNXubEGQg9ueCZ;"  # ← 請自己填入

COMMENT_TEXT = '''我也是患者，歡迎加入異膚社群和大家一起交流！！~
https://line.me/ti/g2/oSdVRcm28E5iu4DfFsOCvTzp6fTPOBXLa3SB9w?utm_source=invitation&utm_medium=link_copy&utm_campaign=default'''

SEARCH_URL = "https://www.threads.net/search?q=異位性皮膚炎"

# 讀取已留言網址
if os.path.exists("commented.json"):
    with open("commented.json", "r") as f:
        commented_posts = set(json.load(f))
else:
    commented_posts = set()

def auto_comment():
    total_posts = 0
    commented_count = 0
    try:
        with sync_playwright() as p:
            print("🚀 啟動瀏覽器")
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = browser.new_context()

            # 加入 Cookie
            context.add_cookies([{
                'name': pair.split('=')[0].strip(),
                'value': pair.split('=')[1].strip(),
                'domain': '.threads.net',
                'path': '/',
                'httpOnly': False,
                'secure': True
            } for pair in THREADS_COOKIE.split(';') if '=' in pair])

            page = context.new_page()
            print("🌐 開啟搜尋頁中...")

            try:
                page.goto(SEARCH_URL, timeout=20000)
                print("✅ 搜尋頁成功載入")
            except Exception as e:
                print(f"❌ Threads 搜尋頁載入失敗: {e}")
                return

            # 模擬滑動加載更多貼文
            for _ in range(5):
                page.mouse.wheel(0, 1500)
                time.sleep(1)

            post_links = []
            articles = page.locator('article').all()
            for article in articles:
            try:
                link = article.locator('a[href*="/@"]').first
                href = link.get_attribute("href")
                if href:
                    post_links.append(href)
            except Exception as e:
                print(f"⚠️ 抓取某篇貼文時錯誤：{e}")
                continue

total_posts = len(post_links)
print(f"🔍 共找到 {total_posts} 則貼文")


total_posts = len(post_links)
print(f"🔍 共找到 {total_posts} 則貼文")

            total_posts = len(post_links)
            print(f"🔍 共找到 {total_posts} 則貼文")

            for link in post_links:
                href = link.get_attribute("href")
                if not href or href in commented_posts:
                    continue

                post_url = f"https://www.threads.net{href}"
                print(f"📌 開啟貼文：{post_url}")
                post_page = context.new_page()

                try:
                    post_page.goto(post_url, timeout=10000)
                    time.sleep(2)
                    content = post_page.locator("article").inner_text(timeout=5000)

                    if "異位性皮膚炎" in content:
                        print("🟢 發現關鍵字，嘗試留言中...")
                        comment_box = post_page.locator("textarea").first
                        comment_box.fill(COMMENT_TEXT)
                        comment_box.press("Enter")
                        print("✅ 留言成功！")
                        commented_count += 1
                        commented_posts.add(href)
                        with open("commented.json", "w") as f:
                            json.dump(list(commented_posts), f)
                    else:
                        print("⏭ 無關鍵字，略過")

                except Exception as e:
                    print(f"⚠️ 貼文處理失敗：{e}")
                finally:
                    post_page.close()
                    time.sleep(2)

            browser.close()

    except Exception as e:
        print("🔥 程式整體錯誤：", e)

    print(f"📊 本次掃描 {total_posts} 篇，成功留言 {commented_count} 篇")
    return total_posts, commented_count



