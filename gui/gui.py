from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (
    QWidget,
    QProgressBar,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QApplication,
)
from PyQt6.QtGui import QShortcut
from PyQt6.QtGui import QKeySequence
import sys


def center_window(window, width, height):
    """計算螢幕中央並將窗口移動到該位置。"""
    screen = (
        QtWidgets.QApplication.primaryScreen().geometry()
    )  # 使用 QScreen 來取代 QDesktopWidget
    x = (screen.width() - width) // 2
    y = (screen.height() - height) // 2
    window.setGeometry(x, y, width, height)


class DownloadProgress(QWidget):
    def __init__(self):
        super().__init__()

        # 設置進度條和布局
        self.layout = QVBoxLayout()

        self.setWindowTitle("啟動進度")
        self.label = QLabel("ChromeDriver 啟動中...")
        self.layout.addWidget(self.label)

        # 設定窗口大小並顯示在螢幕中央
        window_width = 200
        window_height = 100
        center_window(self, window_width, window_height)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)  # 設定進度條範圍為 0 到 100
        self.layout.addWidget(self.progress_bar)

        self.setLayout(self.layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)  # 用來更新進度條的值


class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登入資訊")
        # 使窗口保持在最上方
        self.setWindowFlags(
            self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )

        # 綁定 Cmd+W (Mac) 或 Ctrl+W (其他平台) 關閉窗口
        close_shortcut = QShortcut(
            QKeySequence.StandardKey.Close, self
        )  # 使用 StandardKey
        close_shortcut.activated.connect(self.close)

        # 設定窗口大小並顯示在螢幕中央
        window_width = 400
        window_height = 200
        center_window(self, window_width, window_height)

        # 帳號和密碼輸入框及記住我複選框
        username_label = QtWidgets.QLabel("帳號:")
        self.username_entry = QtWidgets.QLineEdit()
        password_label = QtWidgets.QLabel("密碼:")
        self.password_entry = QtWidgets.QLineEdit()
        self.password_entry.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Password
        )  # 隱藏密碼
        self.remember_me_check = QtWidgets.QCheckBox("記住我")

        self.submit_button = QtWidgets.QPushButton("存檔")
        self.submit_button.setEnabled(False)  # 默認禁用按鈕

        # 設定焦點到帳號輸入框
        self.username_entry.setFocus()

        # 布局
        layout = QtWidgets.QGridLayout()
        layout.addWidget(username_label, 0, 0)
        layout.addWidget(self.username_entry, 0, 1)
        layout.addWidget(password_label, 1, 0)
        layout.addWidget(self.password_entry, 1, 1)
        layout.addWidget(self.remember_me_check, 2, 1)
        layout.addWidget(self.submit_button, 3, 1)

        self.setLayout(layout)

        self.username_entry.textChanged.connect(self.on_input_change)
        self.password_entry.textChanged.connect(self.on_input_change)
        self.submit_button.clicked.connect(self.accept)  # 關閉對話框

        # 聚焦視窗
        self.show()
        self.raise_()

    def on_input_change(self):
        # 根據帳號和密碼的值啟用或禁用按鈕
        if self.username_entry.text() and self.password_entry.text():
            self.submit_button.setEnabled(True)
        else:
            self.submit_button.setEnabled(False)


def get_login_credentials():
    app = QtWidgets.QApplication(sys.argv)
    dialog = LoginDialog()
    dialog.exec()  # 這將顯示對話框並等待用戶輸入

    # 獲取用戶輸入的帳號和密碼
    username = dialog.username_entry.text()
    password = dialog.password_entry.text()
    remember_me = dialog.remember_me_check.isChecked()

    # 不退出應用程式
    app.exit()
    return username, password, remember_me


class UserSelectionWindow(QtWidgets.QWidget):
    def __init__(self, ENVIRONMENT_OPTIONS, SYSTEM_CODE_OPTIONS):
        super().__init__()
        self.ENVIRONMENT_OPTIONS = ENVIRONMENT_OPTIONS
        self.SYSTEM_CODE_OPTIONS = SYSTEM_CODE_OPTIONS
        self.selected_environment = None
        self.selected_system_code = None
        self.branch = ""
        self.grayscale = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("選擇環境與系統代碼")
        # 使窗口保持在最上方
        self.setWindowFlags(
            self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )

        # 綁定 Cmd+W (Mac) 或 Ctrl+W (其他平台) 關閉窗口
        close_shortcut = QShortcut(QKeySequence.StandardKey.Close, self)
        close_shortcut.activated.connect(self.close)

        # 設定窗口大小並顯示在螢幕中央
        window_width = 400
        window_height = 350
        center_window(self, window_width, window_height)

        # 添加 [灰度] Checkbox
        self.grayscale_checkbox = QtWidgets.QCheckBox("灰度")

        # 選擇環境 (用列表顯示)
        environment_label = QtWidgets.QLabel("選擇環境:")
        self.environment_list = QtWidgets.QListWidget()
        self.environment_list.addItems(self.ENVIRONMENT_OPTIONS)
        self.environment_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )
        self.environment_list.currentItemChanged.connect(self.on_selection_change)

        # 選擇系統代碼 (用列表顯示)
        system_code_label = QtWidgets.QLabel("選擇系統代碼:")
        self.system_code_list = QtWidgets.QListWidget()
        self.system_code_list.addItems(self.SYSTEM_CODE_OPTIONS)
        self.system_code_list.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )
        self.system_code_list.currentItemChanged.connect(self.on_selection_change)

        # 顯示 Branch
        branch_label = QtWidgets.QLabel("Branch:")
        self.additional_input_var = QtWidgets.QLineEdit()

        # 確認按鈕 (默認禁用)
        self.submit_button = QtWidgets.QPushButton("確認")
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.submit_selection)

        # 布局
        layout = QtWidgets.QGridLayout()
        layout.addWidget(
            self.grayscale_checkbox, 0, 0, 1, 2
        )  # [灰度] Checkbox放置在頂部，跨兩列
        layout.addWidget(environment_label, 1, 0)
        layout.addWidget(self.environment_list, 1, 1)
        layout.addWidget(system_code_label, 2, 0)
        layout.addWidget(self.system_code_list, 2, 1)
        layout.addWidget(branch_label, 3, 0)
        layout.addWidget(self.additional_input_var, 3, 1)
        layout.addWidget(self.submit_button, 4, 1)

        self.setLayout(layout)
        self.update_additional_input()

    def on_selection_change(self):
        # 當用戶選擇變更時，檢查是否需要啟用按鈕
        if self.environment_list.currentItem() and self.system_code_list.currentItem():
            self.submit_button.setEnabled(True)
        else:
            self.submit_button.setEnabled(False)

        # 更新 Branch placeholder
        self.update_additional_input()

    def update_additional_input(self):
        # 根據 system_code 的值設置前綴
        if self.system_code_list.currentItem():
            prefix = get_branch_prefix(self.system_code_list.currentItem().text())
            self.additional_input_var.setPlaceholderText(prefix)  # 設置placeholder文字
            self.additional_input_var.setText(
                prefix
            )  # 如果希望直接顯示，可以使用 setText

    def submit_selection(self):
        # 確保選擇了環境和系統代碼
        if self.environment_list.currentItem() and self.system_code_list.currentItem():
            prefix = get_branch_prefix(self.system_code_list.currentItem().text())
            user_input = self.additional_input_var.text()

            # 確保前綴只出現一次
            if user_input.startswith(prefix):
                user_input = user_input[len(prefix) :]

            # 包含前綴字串的 branch
            self.branch = prefix + user_input
            self.selected_environment = self.environment_list.currentItem().text()
            self.selected_system_code = self.system_code_list.currentItem().text()
            self.grayscale = self.grayscale_checkbox.isChecked()
            self.close()


def get_user_selection(ENVIRONMENT_OPTIONS, SYSTEM_CODE_OPTIONS):
    app = QtWidgets.QApplication([])  # 創建 PyQt5 應用程式
    window = UserSelectionWindow(
        ENVIRONMENT_OPTIONS, SYSTEM_CODE_OPTIONS
    )  # 創建自定義窗口
    window.show()  # 顯示窗口
    app.exec()  # 啟動主事件循環

    return (
        window.selected_environment,
        window.selected_system_code,
        window.branch,
        window.grayscale,
    )


def get_branch_prefix(system_code):
    """根據系統代碼取得對應前綴"""
    if system_code == "IBK-SSR":
        return "tw-web-bank-ssr/"
    elif system_code == "IBK-A11y":
        return "tw-web-bank-a11y/"
    else:
        return ""


def request_permission_dialog():
    app = QApplication(sys.argv)  # 建立 QApplication 實例
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle("需要完整磁碟存取權限")
    msg_box.setText(
        "應用需要存取一些系統資料，請到 系統偏好設置 > 安全性與隱私 > 完整磁碟存取 中授予權限。"
    )
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


def show_keychain_error_dialog(message):
    app = QApplication(sys.argv)
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Critical)
    error_dialog.setWindowTitle("Keychain Error")
    error_dialog.setText(message)
    error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    error_dialog.exec()


def handle_keychain_locked_error(e):
    show_keychain_error_dialog(f"鑰匙圈未解鎖: {e}")


def handle_keychain_generic_error(e):
    show_keychain_error_dialog(f"鑰匙圈錯誤: {e}")


def show_keychain_error_dialog(message):
    app = QApplication(sys.argv)
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Critical)
    error_dialog.setWindowTitle("Keychain Error")
    error_dialog.setText(message)
    error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    error_dialog.exec()
