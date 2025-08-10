# LINE Bot 聊天優化機器人部署指南

## 功能說明
這是一個 LINE Bot webhook 服務器，具備以下功能：
1. 分階段收集用戶資料（身份、對象、情境、過去對話）
2. 整合 LangChain 和 OpenAI API 生成建議對話
3. 支援 `/more` 指令生成更多內容
4. 支援 `/new` 指令開始新對話
5. 提供對話生成和潤飾兩種模式

## 安裝步驟

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 設置環境變數
複製 `.env.example` 為 `.env` 並填入你的憑證：
```bash
cp .env.example .env
```

編輯 `.env` 檔案：
```
LINE_CHANNEL_ACCESS_TOKEN=你的LINE_CHANNEL_ACCESS_TOKEN
LINE_CHANNEL_SECRET=你的LINE_CHANNEL_SECRET
OPENAI_API_KEY=你的OpenAI_API_KEY
REDIS_URL=redis://localhost:6379/0
```

### 3. 啟動 Redis
確保 Redis 服務正在運行（用於會話管理）：
```bash
# macOS
brew services start redis

# Ubuntu
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis
```

### 4. 運行應用
```bash
python run.py
```

## LINE Bot 設置

1. 在 LINE Developers Console 創建 Bot
2. 取得 Channel Access Token 和 Channel Secret
3. 設置 Webhook URL: `https://你的域名:8080/callback`
4. 啟用 Webhook 和 Use webhook

## 使用方式

1. 用戶輸入 `/new` 開始新對話
2. 系統會分階段詢問：
   - 你是誰？
   - 對話對象是誰？
   - 說話情境是什麼？
   - 過去對話紀錄
3. 選擇模式：
   - 輸入「生成」直接生成對話
   - 輸入「潤飾」提供草稿進行優化
4. 使用 `/more` 生成更多相似內容

## 部署到生產環境

### 使用 Gunicorn
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

### 使用 Docker
創建 Dockerfile：
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 故障排除

1. **Redis 連接失敗**：確保 Redis 服務運行且 REDIS_URL 正確
2. **OpenAI API 錯誤**：檢查 API 密鑰和餘額
3. **LINE Webhook 驗證失敗**：確認 Channel Secret 正確
4. **會話狀態丟失**：檢查 Redis 是否正常工作

## 檔案結構
```
chatbot/
├── app.py              # 主應用程式
├── chat_processor.py   # LangChain 和 OpenAI 整合
├── session_manager.py  # 會話管理
├── requirements.txt    # Python 依賴
├── .env.example       # 環境變數範本
└── run.py             # 啟動腳本
```