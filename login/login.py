# login.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login(driver, username, password, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "login-form-username"))
    ).send_keys(username)
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "login-form-password"))
    ).send_keys(password)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "login-form-submit"))
    ).click()
    print("登入完成")
