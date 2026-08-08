import pystray
from PIL import Image, ImageDraw
import schedule
import time
import threading
import os
from tiktok import send_scheduled_messages

def create_tray_image():
    image = Image.new('RGB', (64, 64), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill=(255, 0, 80))
    draw.rectangle((24, 24, 40, 40), fill=(0, 242, 254))
    return image

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_background_job(users, message, send_time, auto_close, restore_callback):

    def job():
        send_scheduled_messages(users, message)
        if auto_close:
            os._exit(0)

    schedule.every().day.at(send_time).do(job)

    threading.Thread(target=run_schedule, daemon=True).start()

    def show_action(icon, item):
        restore_callback()

    def exit_action(icon, item):
        icon.stop()
        os._exit(0)

    # default=True позволяет разворачивать программу двойным кликом по иконке
    menu = pystray.Menu(
        pystray.MenuItem('Развернуть', show_action, default=True),
        pystray.MenuItem('Выход', exit_action)
    )

    icon = pystray.Icon("TikTokBot", create_tray_image(), "TikTok Auto-Nudge", menu)
    threading.Thread(target=icon.run, daemon=True).start()
