import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from session_manager import SessionManager
from chat_processor import ChatProcessor

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

session_manager = SessionManager()
chat_processor = ChatProcessor(session_manager)

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
    
    if user_message == '/new':
        session_manager.clear_session(user_id)
        reply_text = "開始新的對話！請告訴我：\n1. 你是誰？（例如：我是一個大學生）"
        session_manager.set_state(user_id, 'awaiting_user_identity')
    
    elif user_message == '/more':
        last_prompt = session_manager.get_last_prompt(user_id)
        if last_prompt:
            reply_text = chat_processor.generate_more(last_prompt)
        else:
            reply_text = "沒有找到之前的對話內容。請先開始一個新的對話（輸入 /new）"
    
    else:
        current_state = session_manager.get_state(user_id)
        
        if current_state is None:
            reply_text = "歡迎使用聊天優化機器人！\n\n請輸入 /new 開始新對話\n或輸入 /more 生成更多內容"
        
        elif current_state == 'awaiting_user_identity':
            session_manager.set_user_identity(user_id, user_message)
            session_manager.set_state(user_id, 'awaiting_target_identity')
            reply_text = f"了解，你是：{user_message}\n\n2. 請告訴我對話對象是誰？（例如：我的教授）"
        
        elif current_state == 'awaiting_target_identity':
            session_manager.set_target_identity(user_id, user_message)
            session_manager.set_state(user_id, 'awaiting_context')
            reply_text = f"了解，對象是：{user_message}\n\n3. 請描述對話情境（例如：請教課業問題）"
        
        elif current_state == 'awaiting_context':
            session_manager.set_context(user_id, user_message)
            session_manager.set_state(user_id, 'awaiting_past_conversation')
            reply_text = f"了解，情境是：{user_message}\n\n4. 請提供過去的對話紀錄（如果沒有，請輸入「無」）"
        
        elif current_state == 'awaiting_past_conversation':
            session_manager.set_past_conversation(user_id, user_message)
            session_manager.set_state(user_id, 'awaiting_mode_selection')
            reply_text = "資料收集完成！\n\n請選擇模式：\n1. 輸入「生成」- 我會直接為你生成對話內容\n2. 輸入「潤飾」- 請提供你的對話草稿，我會幫你優化"
        
        elif current_state == 'awaiting_mode_selection':
            if user_message.strip() == '生成':
                session_data = session_manager.get_session_data(user_id)
                reply_text = chat_processor.generate_conversation(session_data, user_id)
                session_manager.set_state(user_id, 'conversation_complete')
            elif user_message.strip() == '潤飾':
                session_manager.set_state(user_id, 'awaiting_draft')
                reply_text = "請提供你的對話草稿："
            else:
                reply_text = "請輸入「生成」或「潤飾」來選擇模式"
        
        elif current_state == 'awaiting_draft':
            session_data = session_manager.get_session_data(user_id)
            reply_text = chat_processor.polish_conversation(session_data, user_message, user_id)
            session_manager.set_state(user_id, 'conversation_complete')
        
        elif current_state == 'conversation_complete':
            reply_text = "對話已完成！\n\n你可以：\n- 輸入 /more 生成更多內容\n- 輸入 /new 開始新對話"
        
        else:
            reply_text = "系統錯誤，請輸入 /new 重新開始"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(debug=False, port=5000)