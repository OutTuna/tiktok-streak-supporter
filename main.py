import flet as ft
import os
from tiktok import get_friends_list
from tray_scheduler import start_background_job

def main(page: ft.Page):
    page.title = "TikTok Streak Keeper"
    page.window.width = 450
    page.window.height = 800
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    selected_users = set()
    is_job_running = False

    title = ft.Text("Сбор данных из TikTok...", size=20, weight="bold")
    progress_ring = ft.ProgressRing()

    friends_list_view = ft.ListView(expand=True, spacing=10)
    friends_container = ft.Container(
        content=friends_list_view,
        width=410,
        height=340,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=10,
        padding=10,
        visible=False
    )

    message_input = ft.TextField(
            label="Текст",
            value="🔥 стрик тайм",
            width=290,
            height=55,
            visible=False
        )

    def format_time(e):
        digits = "".join(filter(str.isdigit, e.control.value))
        digits = digits[:4]
        if len(digits) > 2:
            e.control.value = f"{digits[:2]}:{digits[2:]}"
        else:
            e.control.value = digits
        e.control.update()

    time_input = ft.TextField(
        label="Время",
        value="00:00",
        width=100,
        visible=False,
        on_change=format_time,
        max_length=5,
        counter_text=" "
    )

    close_checkbox = ft.Checkbox(label="Закрыть программу после отправки", value=True, visible=False)

    log_list = ft.ListView(expand=True, spacing=4)
    log_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("История отправок", weight="bold", color=ft.colors.GREY_400),
                ft.Divider(height=1, color=ft.colors.WHITE24),
                log_list
            ]#type: ignore
        ),
        width=410,
        height=140,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=10,
        padding=15,
        bgcolor=ft.colors.with_opacity(0.02, ft.colors.WHITE),
        visible=False
    )

    def update_logs():
        log_list.controls.clear()
        if os.path.exists("nudge_log.txt"):
            with open("nudge_log.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-15:]:
                    log_list.controls.append(
                        ft.Text(line.strip(), size=12, color=ft.colors.GREY_400)
                    )
        else:
            log_list.controls.append(
                ft.Text("Отправок еще не было.", size=12, color=ft.colors.GREY_600)
            )
        page.update()

    def restore_window():
        page.window.visible = True
        page.update()
        update_logs()

    def on_start_click(e):
        nonlocal is_job_running

        if not selected_users:
            page.snack_bar = ft.SnackBar(ft.Text("Выберите хотя бы одного пользователя!"))
            page.snack_bar.open = True
            page.update()
            return

        if not is_job_running:
            start_background_job(
                users=list(selected_users),
                message=message_input.value,
                send_time=time_input.value,
                auto_close=close_checkbox.value,
                restore_callback=restore_window
            )
            is_job_running = True

        page.window.visible = False
        page.update()

    start_btn = ft.ElevatedButton("Свернуть в трей и ждать", on_click=on_start_click, width=410, height=50, visible=False)

    def checkbox_changed(e, username):
        if e.control.value:
            selected_users.add(username)
        else:
            selected_users.discard(username)

    def load_data():
        friends = get_friends_list()

        progress_ring.visible = False
        title.value = f"Найдено диалогов: {len(friends)}"

        friends_list_view.controls.clear()
        for friend in friends:
            is_checked = friend['username'] in selected_users
            friends_list_view.controls.append(
                ft.ListTile(
                    leading=ft.Checkbox(
                        value=is_checked,
                        on_change=lambda e, u=friend['username']: checkbox_changed(e, u)
                    ),
                    title=ft.Text(friend['username'], weight="bold"),
                    trailing=ft.Icon(ft.icons.LOCAL_FIRE_DEPARTMENT, color=ft.colors.GREY_800)
                )
            )

        friends_container.visible = True
        message_input.visible = True
        time_input.visible = True
        close_checkbox.visible = True
        start_btn.visible = True
        log_container.visible = True

        update_logs()

    page.add(
        title,
        progress_ring,
        friends_container,
        ft.Row(
                    [message_input, time_input],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    width=410,
                    spacing=10
                ),        ft.Container(content=close_checkbox, width=410, alignment=ft.alignment.center_left),
        start_btn,
        ft.Container(height=5),
        log_container
    )

    page.update()
    load_data()

if __name__ == "__main__":
    ft.app(target=main)
