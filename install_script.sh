#!/bin/bash

# 設定變數
APP_NAME="fantastic-robot"  # 你的應用名稱
DEST_DIR="$HOME/Applications"  # 安裝目標目錄
TEMP_DIR="/tmp/$APP_NAME"  # 暫存解壓目錄

echo "This script requires administrator privileges to install the app."
sudo -v  # 提前要求用戶輸入密碼來保持會話有效

echo "Fetching the latest release information..."

# 使用 GitHub API 獲取最新版本信息
LATEST_RELEASE=$(curl -s https://api.github.com/repos/ap311036/fantastic-robot/releases/latest)

# 提取 ZIP 文件的下載 URL
ZIP_URL=$(echo "$LATEST_RELEASE" | grep -o "https://.*\.zip" | head -n 1)

if [ -z "$ZIP_URL" ]; then
    echo "Failed to get the latest ZIP URL. Exiting."
    exit 1
fi

echo "Latest ZIP URL: $ZIP_URL"

echo "Downloading $APP_NAME..."s

# 下載 ZIP 文件到暫存目錄
curl -L -o "$TEMP_DIR.zip" "$ZIP_URL"

echo "Unzipping the app..."

# 創建暫存目錄並解壓 ZIP 文件
mkdir -p "$TEMP_DIR"
unzip "$TEMP_DIR.zip" -d "$TEMP_DIR"

echo "Installing the app..."

# 複製解壓後的應用到用戶主目錄中的 Applications 目錄
cp -R "$TEMP_DIR/$APP_NAME.app" "$DEST_DIR/"

# 應用的安裝路徑
INSTALLED_APP="$DEST_DIR/$APP_NAME.app"

echo "Removing quarantine attribute..."

# 移除 quarantine 標記
xattr -d com.apple.quarantine "$INSTALLED_APP" || echo "Failed to remove quarantine attribute."

echo "Setting permissions for the app..."

# 設置應用的權限
sudo chmod -R 755 "$INSTALLED_APP" || echo "Failed to set permissions."

echo "Cleaning up..."

# 刪除暫存文件
rm -rf "$TEMP_DIR" "$TEMP_DIR.zip"

echo "$APP_NAME has been installed and quarantine attribute removed successfully!"
