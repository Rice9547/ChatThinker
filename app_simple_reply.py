import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from chat_processor_fixed import ChatProcessor

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# 簡單的記憶體存儲（避免 Redis 問題）
user_sessions = {}

class SimpleSessionManager:
    def get_session_data(self, user_id):
        return user_sessions.get(user_id, {})
    
    def save_last_prompt(self, user_id, prompt):
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]['last_prompt'] = prompt
    
    def get_last_prompt(self, user_id):
        return user_sessions.get(user_id, {}).get('last_prompt')

session_manager = SimpleSessionManager()
chat_processor = ChatProcessor(session_manager)

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ChatThinker - 簡化版</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 ChatThinker 簡化版</h1>
            <p class="status">✅ 應用程式正在運行中</p>
            <h2>使用方式</h2>
            <p>直接描述你的需求，例如：</p>
            <ul>
                <li>「我是滑板教練，要跟學生說明學費調漲」</li>
                <li>「幫我回覆老闆，明天要請假」</li>
                <li>「怎麼婉拒同事的聚餐邀請」</li>
            </ul>
        </div>
    </body>
    </html>
    """

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    
    if user_message == '/help':
        reply_text = """💡 使用說明：

直接告訴我你的情況，我會提供3個可以直接使用的回覆版本。

範例：
「我是滑板教練，要跟學生說學費要調漲」
「幫我拒絕加班」
「怎麼跟老闆請假」

輸入 /more 可以獲得更多版本"""
    
    elif user_message == '/more':
        last_prompt = session_manager.get_last_prompt(user_id)
        if last_prompt:
            reply_text = chat_processor.generate_more(last_prompt)
        else:
            reply_text = "請先告訴我你的情況"
    
    else:
        # 解析用戶輸入
        context_data = parse_user_input(user_message)
        
        # 生成回覆
        reply_text = chat_processor.generate_conversation(context_data, user_id)
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def parse_user_input(message):
    """從自然語言解析出對話要素"""
    data = {
        'user_identity': '',
        'target_identity': '',
        'context': message,
        'past_conversation': '無'
    }
    
    # 簡單的關鍵字解析
    if '我是' in message:
        parts = message.split('我是')
        if len(parts) > 1:
            identity_part = parts[1].split('，')[0].split('，')[0]
            data['user_identity'] = identity_part.strip()
    
    # 解析對象
    if '跟' in message or '向' in message or '對' in message:
        for keyword in ['跟', '向', '對']:
            if keyword in message:
                parts = message.split(keyword)
                if len(parts) > 1:
                    target_part = parts[1].split(' ')[0].split('說')[0].split('，')[0]
                    data['target_identity'] = target_part.strip()
                break
    
    # 如果沒有明確身份，根據情境推測
    if not data['user_identity']:
        if '教練' in message:
            data['user_identity'] = '教練'
        elif '老師' in message:
            data['user_identity'] = '老師'
        elif '員工' in message or '請假' in message:
            data['user_identity'] = '員工'
        else:
            data['user_identity'] = '我'
    
    if not data['target_identity']:
        if '學生' in message:
            data['target_identity'] = '學生'
        elif '老闆' in message or '主管' in message:
            data['target_identity'] = '主管'
        elif '同事' in message:
            data['target_identity'] = '同事'
        elif '客戶' in message:
            data['target_identity'] = '客戶'
        else:
            data['target_identity'] = '對方'
    
    return data

if __name__ == "__main__":
    app.run(debug=False, port=8000)