#!/bin/bash

# 設定變數
UPDATE_URL="$1"  # 更新包的下載 URL，由參數傳遞
VERSION="$2"     # 版本號，由參數傳遞
DEST_DIR="$HOME/Applications"  # 應用安裝目標目錄
TEMP_DIR="/tmp/app_update"  # 暫存下載的目錄
ZIP_FILE="/tmp/app_update.zip"  # ZIP 文件的下載路徑

# 顯示下載進度並下載 ZIP 文件
echo "Downloading new version ${VERSION}..."
curl -L -o "$ZIP_FILE" "$UPDATE_URL" --progress-bar

# 確認下載是否成功
if [ $? -ne 0 ]; then
    echo "下載失敗。"
    exit 1
fi

# 創建臨時目錄並解壓 ZIP 文件
echo "Unzipping the app..."
mkdir -p "$TEMP_DIR"
unzip "$ZIP_FILE" -d "$TEMP_DIR"

# 檢查解壓是否成功
if [ $? -ne 0 ]; then
    echo "解壓失敗。"
    exit 1
fi

# 找到解壓後的應用文件
NEW_APP_PATH="$TEMP_DIR/fantastic-robot.app"
if [ ! -d "$NEW_APP_PATH" ]; then
    echo "未找到應用程式包: $NEW_APP_PATH"
    exit 1
fi

# 移動新版本到應用目錄
echo "Installing the new version..."
cp -R "$NEW_APP_PATH" "$DEST_DIR/"

# 檢查安裝是否成功
if [ $? -ne 0 ]; then
    echo "安裝失敗。"
    exit 1
fi

# 設置新應用的執行權限
echo "Setting permissions..."
chmod -R 755 "$DEST_DIR/fantastic-robot.app"

# 檢查權限設置是否成功
if [ $? -ne 0 ]; then
    echo "設置權限失敗。"
    exit 1
fi

# 清理臨時文件
echo "Cleaning up..."
rm -rf "$TEMP_DIR" "$ZIP_FILE"

# 自動啟動應用
echo "Launching the app..."
open "$DEST_DIR/fantastic-robot.app"

echo "Update to version $VERSION installed and launched successfully!"
