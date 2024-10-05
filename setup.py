from struct import pack
from setuptools import setup, find_packages
from datetime import datetime

# 動態生成當前日期
current_date = datetime.now().strftime("%Y-%m-%d")

APP = ["main.py"]  # APP 啟動的 Python 檔案
DATA_FILES = [
    "./driver_setup/driver_setup.py",
    "./gui/gui.py",
    "./issue_creation/issue_creation.py",
    "./login/login.py",
    "./credentials/credentials.py",
    "./send_notification/send_notification.py",
    "./check_update/check_update.py",
    "./utils/utils.py",
    "./config.py",
]  # 自定義的模組放在 DATA_FILES 列表中
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "512-mac.png",  # APP 圖標
    "includes": [
        "keyring.backends.kwallet",
        "keyring.backends.OS_X",
        "keyring.backends.macOS",
        "keyring.backends.libsecret",
        "keyring.backends.SecretService",
        "keyring.backends.chainer",
        "keyring.backends.Windows",
    ],
    # "packages": [],  # 第三方庫放在 OPTIONS 下的 includes 對應的列表中
    "plist": {
        "LSBackgroundOnly": True,
        "LSUIElement": True,
        "NSAppTransportSecurity": {"NSAllowsArbitraryLoads": True},
        "NSUserNotificationAlertStyle": "alert",  # 可以設置為 'banner' 或 'alert'
        "CFBundleShortVersionString": "0.1.0",
        "NSHumanReadableCopyright": "Snoop © 2024",
        "CFBundleVersion": f"{current_date}-0.1.0",  # 動態生成的日期
        "CFBundleShortVersionString": f"{current_date}-0.1.0",  # 動態生成的日期
    },
}


setup(
    app=APP,
    data_files=DATA_FILES,
    packages=find_packages(),
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=[
        "selenium",
        "pyperclip",
        "webdriver-manager",
        "keyring",
        "PyQt6",
        "rumps",
        "requests",
    ],
)

# 第二种配置
# from setuptools import setup

# APP = ["snoop.py"]  # APP启动的py文件
# DATA_FILES = []  # 自写模块放在DATA_FILES列表中
# OPTIONS = {
#     "includes": ["requests"],  # 第三方库放在OPTIONS下的includes对应的列表中
#     "iconfile": "Icon.icns",  # APP图标
#     "plist": {"CFBundleShortVersionString": "0.1.0"},  # APP 版本
# }

# setup(
#     app=APP,
#     data_files=DATA_FILES,
#     options={"py2app": OPTIONS},
#     setup_requires=["py2app"],
#     py_modules=["test", "test2"],  # 项目modules内容
# )
