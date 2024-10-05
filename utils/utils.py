# utils.py

from datetime import datetime, timedelta


def generate_summary(environment_name, system_code):
    # 獲取當前時間
    now = datetime.now()

    # 向後推一小時
    future_time = now + timedelta(hours=1)

    # 格式化日期和時間
    date_str = future_time.strftime("%Y%m%d")  # 年月日
    hour_str = future_time.strftime("%H")  # 小時部分

    # 構造最終字串
    summary = (
        f"[{environment_name}] 程式上線作業申請單 {system_code}_{date_str}{hour_str}00"
    )

    return summary
