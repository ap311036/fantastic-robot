# main.py
import sys
import time
import rumps
import webbrowser
import logging
from check_update.check_update import check_for_updates_and_download
from send_notification.send_notification import send_notification
from driver_setup.driver_setup import setup_driver
from login.login import login
from issue_creation.issue_creation import (
    create_issue,
    add_link,
    check_jira_ticket_status,
)
from gui.gui import get_user_selection, get_login_credentials
from credentials.credentials import (
    load_credentials,
    save_credentials,
    credentials_exist,
    delete_credentials,
)
from config import (
    ENVIRONMENT_OPTIONS,
    SYSTEM_CODE_OPTIONS,
    url,
    use_keychain,
)

# 配置 logging
logging.basicConfig(
    level=logging.INFO,  # 可以根據需要改為 DEBUG 或 ERROR 等
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "app.log", encoding="utf-8"
        ),  # 將日誌輸出到 app.log 文件，並設置編碼為 utf-8
        logging.StreamHandler(sys.stdout),  # 在控制台輸出日誌，並設置輸出到 stdout
    ],
)

# 取得 logger 實例
logger = logging.getLogger(__name__)


def main():
    # 檢查是否有儲存的帳號密碼
    if credentials_exist(use_keychain):
        username, password = load_credentials(use_keychain)
    else:
        username, password, remember_me = get_login_credentials()

        # 如果使用者關閉了環境選擇視窗而沒有選擇，則退出流程
        if not username or not password:
            rumps.alert("操作取消：未輸入使用者帳號及密碼")
            return
        if remember_me:
            save_credentials(username, password, use_keychain)

    # 獲取環境、系統代碼及分支資訊
    environment_name, system_code, branch, grayscale = get_user_selection(
        ENVIRONMENT_OPTIONS, SYSTEM_CODE_OPTIONS
    )
    print(f"選擇: {environment_name}, {system_code}")
    print(f"Branch: {branch}")
    print("是灰度" if grayscale else "不是灰度")

    # 如果使用者關閉了環境選擇視窗而沒有選擇，則退出流程
    if not environment_name or not system_code:
        rumps.alert("操作取消：未選擇環境或系統代碼")
        return

    driver = setup_driver()
    try:
        issue_url = login(driver, username, password, url)
        issue_url = create_issue(driver, environment_name, system_code, branch)
        # if grayscale:
        #     # add_link(driver, environment_name, system_code)
        #     check_jira_ticket_status(driver, environment_name)
        print("問題創建完成")

        webbrowser.open(issue_url)  # 使用預設瀏覽器打開連結

    except Exception as e:
        print(f"發生異常：{e}")
        time.sleep(3)
        driver.quit()
        rumps.alert("發生異常：問題創建失敗")


class AwesomeStatusBarApp(rumps.App):
    def __init__(self):
        super(AwesomeStatusBarApp, self).__init__("LBTW")
        self.menu = ["開單", None, "Delete Credential", "Silly button"]

    @rumps.clicked("開單")
    def prefs(self, _):
        main()

    # @rumps.clicked("Silly button")
    # def onoff(self, sender):
    #     sender.state = not sender.state

    @rumps.clicked("Delete Credential")
    def sayhi(self, _):
        delete_credentials(use_keychain)
        send_notification("刪除帳號密碼", "Delete Credentials", "Success!")
        # rumps.notification()

    # def disable_notification(self):
    #     # 禁用 Notification 菜单项
    #     print(self.notification_item)
    #     self.notification_item.set_callback(None)  # 移除回调
    #     self.notification_item.state = False

    # def enable_notification(self):
    #     # 启用 Notification 菜单项
    #     self.notification_item.set_callback(self.sayhi)
    #     self.notification_item.state = False  # 取消禁用视觉效果


if __name__ == "__main__":
    logger.info("應用程式啟動")
    # 在這裡檢查更新並確保所有的設定完成後，才啟動 Rumps 應用
    check_for_updates_and_download()
    AwesomeStatusBarApp().run()
