# credentials/credentials.py
import json
import os
import keyring
import logging
from keyring.errors import KeyringLocked, KeyringError
from gui.gui import (
    request_permission_dialog,
    handle_keychain_locked_error,
    handle_keychain_generic_error,
    show_keychain_error_dialog,
)

logger = logging.getLogger(__name__)

CREDENTIALS_FILE = "credentials.json"
SERVICE_NAME = "SnoopApp"  # Keychain/密碼管理工具的服務名稱


def load_credentials_from_file():
    """
    從本地憑證文件中載入使用者名稱，若不存在則返回 None.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        logger.info("無法找到憑證文件")
        return None

    try:
        with open(CREDENTIALS_FILE, "r") as file:
            return json.load(file)
    except PermissionError:
        logger.error("讀取憑證文件時無權限")
        request_permission_dialog()
        return None
    except json.JSONDecodeError:
        logger.error("無法解析憑證文件")
        return None


def save_credentials_to_file(credentials):
    """
    將憑證保存到本地檔案.
    """
    try:
        with open(CREDENTIALS_FILE, "w") as file:
            json.dump(credentials, file)
        logger.info("憑證已成功保存到本地檔案")
    except PermissionError:
        logger.error("保存憑證時無權限")
        request_permission_dialog()
    except Exception as e:
        logger.error(f"保存憑證時發生錯誤: {e}")


def save_credentials(username, password, use_keychain=True):
    """
    將使用者名稱和密碼保存到本地檔案或 macOS 的 Keychain 中.
    """
    credentials = {"username": username}
    save_credentials_to_file(credentials)

    if use_keychain:
        try:
            keyring.set_password(SERVICE_NAME, username, password)
            logger.info(f"已將使用者名稱 {username} 和密碼存入 Keychain 中")
        except keyring.errors.PasswordSetError as e:
            show_keychain_error_dialog(f"無法將密碼存入 Keychain: {e}")
            logger.error(f"無法將密碼存入 Keychain: {e}")
    else:
        # 在本地文件中保存密碼
        credentials["password"] = password
        save_credentials_to_file(credentials)
        logger.info(f"已將使用者名稱 {username} 和密碼存入本地檔案中")


def load_credentials(use_keychain=True):
    """
    從本地檔案或 macOS 的 Keychain 中載入使用者名稱和密碼.
    """
    credentials = load_credentials_from_file()
    if not credentials:
        logging.warning("無法找到本地憑證文件")
        return None, None

    username = credentials.get("username")
    if not username:
        logging.warning("無法找到使用者名稱")
        return None, None

    if use_keychain:
        try:
            password = keyring.get_password(SERVICE_NAME, username)
            if password:
                logger.info(f"從 Keychain 載入使用者名稱 {username}")
                return username, password
            else:
                logging.warning(f"無法從 Keychain 中找到使用者名稱 {username}")
                return None, None
        except KeyringLocked as e:
            handle_keychain_generic_error(e)
            logger.error(f"Keychain 鎖定錯誤: {e}")
        except KeyringError as e:
            handle_keychain_locked_error(e)
            logger.error(f"Keychain 錯誤: {e}")
        return None, None
    else:
        password = credentials.get("password")
        if password:
            return username, password
        else:
            logging.warning("無法從本地檔案中找到密碼")
            return None, None


def credentials_exist(use_keychain=True):
    """
    檢查是否存在保存的憑證.
    """
    logger.info("檢查是否存在保存的憑證.")
    credentials = load_credentials_from_file()
    if not credentials or "username" not in credentials:
        logging.warning("無法找到本地憑證或使用者名稱")
        return False

    username = credentials["username"]
    if use_keychain:
        try:
            return keyring.get_password(SERVICE_NAME, username) is not None
        except KeyringLocked as e:
            handle_keychain_generic_error(e)
            logger.error(f"Keychain 鎖定錯誤: {e}")
            return False
        except KeyringError as e:
            handle_keychain_locked_error(e)
            logger.error(f"Keychain 錯誤: {e}")
            return False
    else:
        return "password" in credentials


def delete_credentials(use_keychain=True):
    """
    刪除保存的憑證.
    """
    credentials = load_credentials_from_file()
    if not credentials or "username" not in credentials:
        logging.warning("無法找到本地憑證或使用者名稱")
        return

    username = credentials["username"]

    if use_keychain:
        keyring.delete_password(SERVICE_NAME, username)
        logger.info(f"已刪除 Keychain 中的使用者名稱 {username} 和密碼")

    if os.path.exists(CREDENTIALS_FILE):
        os.remove(CREDENTIALS_FILE)
        logger.info("已刪除本地檔案中的憑證")

