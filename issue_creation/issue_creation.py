# issue_creation.py
import pyperclip
import rumps
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from utils.utils import generate_summary

system_code_to_value = {
    "BOF_WEB": "14400",
    "CWA": "11107",
    "IBK": "11108",
    "IBK-SSR": "11108",
    "IBK-A11y": "11108",
}

jira_urls = {
    "CWA": {
        "STG": "PRD-22741",
        "UAT": "PRD-22740",
    },
    "IBK": {
        "STG": "PRD-22739",
        "UAT": "PRD-22738",
    },
    "BOF_WEB": {
        "STG": "PRD-24319",
        "UAT": "PRD-24323",
    },
}


def create_issue(driver, environment_name, system_code, branch=""):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "create_link"))
    ).click()
    dialog = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "create-issue-dialog"))
    )

    summary = generate_summary(environment_name, system_code)

    click_release_option(driver, "project-field", "LBTW-PRD (PRD)")
    click_release_option(
        driver, "issuetype-field", f"{environment_name} Release"
    )  # 使用 environment_name

    fill_text_field(driver, "summary", summary)
    fill_select_field(driver, "customfield_12100", "12804")

    select_value = system_code_to_value[system_code]
    fill_select_field(driver, "customfield_10668", select_value)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "assign-to-me-trigger"))
    ).click()
    click_calendar(driver)
    fill_text_field(driver, "customfield_11901", branch)
    
    return "https://www.example.com"


def click_release_option(driver, field_id, text):
    try:
        field_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, field_id))
        )

        current_value = field_input.get_attribute("value")
        if current_value == text:
            print(f"Input already has the value: {current_value}")
        else:
            print(f"Current value: {current_value}, changing to {text}")
            field_input.click()

            xpath_selector = f"//a[text()='{text}']"

            release_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector))
            )
            release_option.click()
            print(f"Clicked {text}")
    except Exception as e:
        print(f"Error occurred: {e}")


def fill_text_field(driver, field_id, text):
    try:
        text_field = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, field_id))
        )
        text_field.clear()
        text_field.send_keys(text)

    except Exception as e:
        print(f"Error: {field_id}, {e}")


def fill_select_field(driver, field_id, value):
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, field_id))
        )
        select = Select(select_element)
        select.select_by_value(value)

    except Exception as e:
        print(f"Error: {field_id}, {e}")


def click_calendar(driver):
    try:
        trigger_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "customfield_10300-trigger"))
        )
        trigger_element.click()

        calendar_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "calendar"))
        )

        today_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class, 'calendar')]//td[contains(@class, 'today')]",
                )
            )
        )

        today_element.click()

    except Exception as e:
        print(f"An error occurred: {e}")


def add_link(driver, environment_name, system_code):
    jira_ticket = get_jira_ticket(environment_name, system_code)
    print(jira_ticket)

    # 點擊More按鈕
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "opsbar-operations_more"))
    ).click()

    # 等待dropdown菜單出現
    dropdown_locator = (By.ID, "opsbar-operations_more_drop")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(dropdown_locator))

    # 使用XPath找到文字內容為"Link"的元素並點擊
    link_locator = (By.XPATH, "//a//span[text()='Link']")
    link_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(link_locator)
    )
    link_element.click()

    # 等待 id="link-issue-dialog" 的 dialog 出現
    dialog_locator = (By.ID, "link-issue-dialog")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(dialog_locator))

    # 等待 id="link-type" 的 select 元素出現
    select_locator = (By.ID, "link-type")
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(select_locator)
    )

    # 創建一個 Select 實例並選擇 value 為 "contains"
    select = Select(select_element)
    select.select_by_value("contains")

    # 定位 id 為 "jira-issue-keys-textarea" 的 textarea
    textarea_locator = (By.ID, "jira-issue-keys-textarea")
    textarea_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(textarea_locator)
    )

    # 填入參數 jira_ticket
    textarea_element.send_keys(jira_ticket)
    # 執行 JavaScript 移除 textarea 的焦點
    driver.execute_script("arguments[0].blur();", textarea_element)

    # 使用xpath來找到Link按鈕
    link_button = driver.find_element(
        By.XPATH, "//input[@type='submit' and @value='Link']"
    )

    # 點擊Link按鈕
    # link_button.click()


def copy_current_url(driver):
    # 獲取當前網址
    current_url = driver.current_url

    # 將網址複製到剪貼簿
    pyperclip.copy(current_url)

    # 確認複製成功
    print("當前網址已複製到剪貼簿:", current_url)


def get_jira_ticket(environment_name, system_code):
    # 處理 IBK 類型的 system_code
    if system_code.startswith("IBK"):
        system_code = "IBK"

    # 根據 system_code 和 environment_name 獲取對應的 TICKET
    return jira_urls.get(system_code, {}).get(environment_name, "無對應的 JIRA TICKET")


def check_jira_ticket_status(driver, environment_name):
    # 等待包含狀態的元素出现
    status_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "span.jira-issue-status-lozenge")
        )
    )

    # 捕獲 status_element
    status_text = status_element.text

    # 定義環境與狀態的對應文字
    expected_status = {"STG": "WAIT FOR STG", "UAT": "WAIT FOR UAT"}

    # 檢查當前環境的預期狀態
    if environment_name in expected_status:
        if status_text == expected_status[environment_name]:
            print(f"狀態為 {status_text}")
        else:
            print(
                f"狀態不是 {expected_status[environment_name]}，當前狀態為 {status_text}"
            )
            rumps.alert(
                "灰度單：請確認灰度單狀態是否正確",
                f"狀態不是 {expected_status[environment_name]}，當前狀態為 {status_text}",
            )
    else:
        print("未知的 environment_name")
