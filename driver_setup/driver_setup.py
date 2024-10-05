import time
from PyQt6.QtCore import QThread, pyqtSignal, QEventLoop, QObject
from PyQt6.QtWidgets import QApplication
from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.driver_cache import DriverCacheManager
from gui.gui import DownloadProgress
import sys
import subprocess


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    download_finished = pyqtSignal(str)  # 發射 driver 路徑的信號

    def __init__(self, driver_manager):
        super().__init__()
        self.driver_manager = driver_manager

    def run(self):
        # 模擬下載進度
        for i in range(1, 101):  # 模擬 100 個步驟的進度
            self.progress.emit(i)
            time.sleep(0.05)  # 每個步驟等待 50ms (可以根據實際需要調整)

        try:
            driver_path = self.driver_manager.install()  # 安裝並獲取 ChromeDriver 路徑
            self.download_finished.emit(driver_path)  # 發射下載完成信號，傳遞路徑
        except Exception as e:
            print(f"下載過程中發生錯誤: {e}")


class DriverContainer(QObject):
    def __init__(self):
        super().__init__()
        self.driver = None  # 用於存儲 WebDriver 實例


def get_local_chrome_version():
    chrome_paths = {
        "linux": "/usr/bin/google-chrome",
        "darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    }

    chrome_path = chrome_paths.get(sys.platform)

    if chrome_path:
        try:
            result = subprocess.run(
                [chrome_path, "--version"], capture_output=True, text=True
            )
            version = result.stdout.split()[2]  # 提取版本號
            return version
        except Exception as e:
            print(f"無法獲取 Chrome 版本: {e}")
            return None
    else:
        print(f"不支援的平台: {sys.platform}")
        return None


def setup_driver():
    app = QApplication(sys.argv)

    # 創建進度條對話框
    progress_window = DownloadProgress()
    progress_window.show()

    local_chrome_version = get_local_chrome_version()

    if local_chrome_version:
        print(f"本地 Chrome 版本: {local_chrome_version}")
        driver_manager = ChromeDriverManager(driver_version=local_chrome_version)
    else:
        print("無法檢測本地 Chrome 版本，下載最新的 chromedriver。")
        driver_cache_manager = DriverCacheManager(
            root_dir="chrome_drivers_cache", valid_range=2
        )
        driver_manager = ChromeDriverManager(cache_manager=driver_cache_manager)

    download_thread = DownloadThread(driver_manager)

    # 創建 DriverContainer 來存儲 driver 實例
    driver_container = DriverContainer()

    # 創建一個事件循環，用於等待下載完成
    loop = QEventLoop()

    def on_download_finished(driver_path):
        print(f"Chrome 將安裝在: {driver_path}")

        # 關閉進度視窗
        progress_window.close()

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("detach", True)
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }
        options.add_experimental_option("prefs", prefs)

        # 使用下載的 ChromeDriver 路徑創建 driver 實例
        driver_container.driver = webdriver.Chrome(
            service=ChromeService(driver_path), options=options
        )
        print(f"ChromeDriver 已啟動，路徑: {driver_path}")

        # 開始檢查視窗是否關閉
        # check_window_closed(driver_container.driver)

        # 停止事件循環
        loop.exit()  # 退出事件循環

    # 當下載進度更新時，連接到 update_progress 方法
    download_thread.progress.connect(progress_window.update_progress)
    download_thread.download_finished.connect(on_download_finished)

    # 啟動下載線程
    download_thread.start()

    # 啟動事件循環，直到下載完成後 `loop.exit()` 退出
    loop.exec()

    # 返回存儲在 driver_container 中的 driver 實例
    return driver_container.driver


def check_window_closed(driver):
    """檢查 ChromeDriver 視窗是否關閉的函數。"""
    try:
        while True:
            time.sleep(1)  # 每秒檢查一次
            # 檢查視窗是否仍然存在
            if driver.window_handles:
                # 獲取當前視窗的標題以確認視窗仍然存在
                current_title = driver.title
                print("當前視窗標題:", current_title)
            else:
                print("視窗已關閉！")
                break  # 退出循環
    except NoSuchWindowException:
        print("視窗已關閉！")
    except Exception as e:
        print(f"發生異常: {str(e)}")
    finally:
        try:
            driver.quit()  # 確保關閉 WebDriver
        except Exception as e:
            print(f"關閉 WebDriver 時發生異常: {str(e)}")
