import os
from datetime import datetime
from playwright.sync_api import sync_playwright

SESSION_DIR = os.path.abspath("./tiktok_session")

FAST_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-background-networking"
]

def get_friends_list():
    friends = []

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            SESSION_DIR,
            headless=False,
            channel="chrome",
            args=FAST_ARGS,
            ignore_default_args=["--enable-automation"]
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["media", "font"] else route.continue_())
        page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded")

        while "login" in page.url:
            page.wait_for_timeout(1000)

        if "messages" not in page.url:
            page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded")

        chat_items = page.locator('div[data-e2e="dm-new-conversation-item"]')
        try:
            chat_items.first.wait_for(timeout=10000)
        except:
            pass

        count = chat_items.count()
        for i in range(count):
            item = chat_items.nth(i)
            username_locator = item.locator('p[data-e2e="dm-new-conversation-nickname"]')
            username = username_locator.inner_text() if username_locator.count() > 0 else f"user_{i}"
            friends.append({"username": username})

        if not friends:
            friends = [
                {"username": "sanya_pepe"},
                {"username": "dota_enjoyer"},
            ]

        browser.close()
    return friends

def send_scheduled_messages(users, message):
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            SESSION_DIR,
            headless=True,
            channel="chrome",
            args=FAST_ARGS,
            ignore_default_args=["--enable-automation"]
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "media", "font", "stylesheet"] else route.continue_())

        page.goto("https://www.tiktok.com/messages", wait_until="domcontentloaded")

        try:
            page.locator('div[data-e2e="dm-new-conversation-item"]').first.wait_for(timeout=10000)
        except:
            pass

        for user in users:
            try:
                user_element = page.locator('p[data-e2e="dm-new-conversation-nickname"]').get_by_text(user, exact=True)

                if user_element.count() == 0:
                    raise Exception("Диалог не найден в списке")

                user_element.first.click()

                editor = page.locator("div[contenteditable='true']")
                editor.wait_for(state="visible", timeout=5000)
                editor.click()
                editor.fill(message)
                page.wait_for_timeout(300)

                editor.press("Enter")

                success_msg = f"{user} : сообщение отправлено"
                print(success_msg)

                with open("nudge_log.txt", "a", encoding="utf-8") as f:
                    time_now = datetime.now().strftime("%d.%m %H:%M")
                    f.write(f"[{time_now}] {success_msg}\n")

                page.wait_for_timeout(1000)
            except Exception as e:
                error_msg = f"{user} : ошибка отправки"
                print(f"{error_msg} ({e})")

                with open("nudge_log.txt", "a", encoding="utf-8") as f:
                    time_now = datetime.now().strftime("%d.%m %H:%M")
                    f.write(f"[{time_now}] {error_msg}\n")

        browser.close()
