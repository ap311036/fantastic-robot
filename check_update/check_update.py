import stat
import requests
import os
import zipfile
import shutil
import sys
import rumps
from PyQt6 import QtWidgets, QtCore
from config import CURRENT_VERSION
import AppKit


def focus_alert():
    app = AppKit.NSApplication.sharedApplication()
    app.activateIgnoringOtherApps_(True)


def check_for_updates(current_version):
    # GitHub API 的 URL，替換 {owner} 和 {repo} 為你的 GitHub 倉庫
    owner = "ap311036"
    repo = "fantastic-robot"
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        latest_release = response.json()
        latest_version = latest_release["tag_name"]
        print(f"最新版本：{latest_version}")
        print(f"當前版本：{current_version}")
        if latest_version > current_version:
            # 如果最新版本大於當前版本，返回更新訊息
            return latest_release["assets"][0]["browser_download_url"], latest_version
    return None, None


def check_for_updates_and_download():
    try:
        download_url, latest_version = check_for_updates(CURRENT_VERSION)

        if download_url:
            print(f"發現新版本：{latest_version}，準備下載更新")
            download_update(download_url, latest_version)
        else:
            print("當前是最新版本")

    except requests.RequestException as e:
        print(f"檢查更新失敗: {e}")


def download_update(update_url, version):
    # 創建應用程序對象
    app = QtWidgets.QApplication(sys.argv)

    # 創建進度條對話框
    progress_dialog = QtWidgets.QProgressDialog(f"新版本{version}下載中...", "取消", 0, 100)
    progress_dialog.setWindowTitle("更新下載")
    progress_dialog.setWindowModality(
        QtCore.Qt.WindowModality.WindowModal
    )  # 修改為 PyQt6
    progress_dialog.show()

    try:
        # 下載更新包
        response = requests.get(update_url, stream=True)
        response.raise_for_status()

        # 獲取文件總大小
        total_size = int(response.headers.get("content-length", 0))

        # 存儲位置
        update_path = os.path.join("/tmp", "app_update.zip")
        downloaded_size = 0

        # 開始下載並更新進度條
        with open(update_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)

                # 計算進度百分比並更新進度條
                progress = int(downloaded_size / total_size * 100)
                progress_dialog.setValue(progress)

                # 如果用戶點擊取消
                if progress_dialog.wasCanceled():
                    print("下載已取消")
                    return

        # 下載完成，安裝更新
        install_update(update_path)

    except requests.RequestException as e:
        print(f"下載更新失敗: {e}")
    finally:
        # 關閉進度條對話框
        progress_dialog.close()
        sys.exit(app.exec())  # PyQt6 中去掉 exec_()


def install_update(update_path):
    try:
        extract_dir = os.path.join("/tmp", "app_update")
        with zipfile.ZipFile(update_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        extracted_files = os.listdir(extract_dir)
        print(f"解壓後的檔案: {extracted_files}")

        new_app_path = os.path.join(extract_dir, "main.app")
        if not os.path.exists(new_app_path):
            raise FileNotFoundError(f"未找到應用程式包: {new_app_path}")

        current_app_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
        )
        print(f"當前應用路徑: {current_app_path}")

        backup_path = current_app_path + "_backup"
        shutil.move(current_app_path, backup_path)

        shutil.move(new_app_path, current_app_path)

        executable_path = os.path.join(current_app_path, "Contents", "MacOS", "main")
        set_permissions(executable_path)

        shutil.rmtree(backup_path)
        shutil.rmtree(extract_dir)
        os.remove(update_path)

        rumps.alert("更新成功，懩用程式即將重啟。", "若無自動開啟，請手動開啟。")
        restart_app()

    except Exception as e:
        print(f"安裝更新失敗: {e}")
        rumps.alert("更新失敗，請重試。")


def set_permissions(executable_path):
    try:
        st = os.stat(executable_path)
        os.chmod(executable_path, st.st_mode | stat.S_IEXEC)
        print(f"成功修正權限: {executable_path}")
    except Exception as e:
        print(f"修正權限失敗: {e}")


def restart_app():
    os.execl(sys.executable, sys.executable, *sys.argv)
