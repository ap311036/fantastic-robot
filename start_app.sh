#!/bin/bash

echo "This script requires administrator privileges to install the app."
sudo -v  # 提前要求用戶輸入密碼來保持會話有效

# 动态获取当前应用程序路径
APP_PATH="$1"  # 从参数获取应用路径

# 移除隔离标记
xattr -d com.apple.quarantine "$APP_PATH"

# 设置权限
sudo chmod -R 755 "$APP_PATH"

# 启动应用程序
open "$APP_PATH"
