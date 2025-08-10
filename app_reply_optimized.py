import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    PostbackEvent, QuickReply, QuickReplyButton, 
    MessageAction, PostbackAction
)
from dotenv import load_dotenv
from session_manager import SessionManager
from reply_generator import ReplyGenerator
from flex_message_builder import FlexMessageBuilder
import urllib.parse

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

session_manager = SessionManager()
reply_generator = ReplyGenerator()
flex_builder = FlexMessageBuilder()

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
    
    if user_message == '/start' or user_message == '開始':
        # 顯示快速情境選單
        flex_message = flex_builder.create_quick_scenarios_menu()
        line_bot_api.reply_message(event.reply_token, flex_message)
        return
    
    elif user_message == '/help' or user_message == '說明':
        reply_text = """💡 ChatThinker 使用說明

我能幫你快速生成合適的回覆文字！

【使用方式】
1️⃣ 輸入 /start 選擇情境
2️⃣ 直接描述你的情況
3️⃣ 獲得3個回覆選項

【範例】
「幫我回覆老闆，明天要請假」
「怎麼拒絕同事的飯局邀請」
「催客戶交文件要怎麼說」

【特色】
✅ 直接給答案，不囉嗦
✅ 提供3種語氣選擇
✅ 一鍵複製使用
✅ 可調整語氣"""
        
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="開始使用", text="/start")),
            QuickReplyButton(action=MessageAction(label="看範例", text="看範例"))
        ])
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text, quick_reply=quick_reply)
        )
        return
    
    elif user_message == '看範例':
        reply_text = """📝 使用範例：

【範例1】
你：幫我回覆老闆明天請假
我：[立即顯示3個選項卡片]

【範例2】  
你：怎麼拒絕加班
我：[立即顯示3個選項卡片]

【範例3】
你：催進度要怎麼說比較好
我：[立即顯示3個選項卡片]

每個卡片都可以：
- 直接複製使用 📋
- 調整語氣 ✏️"""
        
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="馬上試試", text="/start"))
        ])
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text, quick_reply=quick_reply)
        )
        return
    
    elif user_message == '我要自訂情境':
        session_manager.set_state(user_id, 'custom_scenario')
        
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="請假", text="幫我寫請假訊息")),
            QuickReplyButton(action=MessageAction(label="道歉", text="幫我寫道歉訊息")),
            QuickReplyButton(action=MessageAction(label="拒絕", text="幫我婉拒邀請")),
            QuickReplyButton(action=MessageAction(label="催促", text="幫我催進度"))
        ])
        
        reply_text = "請描述你的情況，例如：\n\n「幫我回覆老闆，明天要請假看醫生」\n「怎麼婉拒同事的聚餐邀請」\n「提醒客戶該付款了」"
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text, quick_reply=quick_reply)
        )
        return
    
    else:
        # 處理自然語言輸入
        context_data = _extract_context_from_message(user_message)
        
        # 生成回覆選項
        options = reply_generator.generate_reply_options(context_data)
        
        # 建立 Flex Message
        flex_message = flex_builder.create_reply_options_carousel(options)
        
        # 發送回覆
        line_bot_api.reply_message(event.reply_token, flex_message)

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    data = event.postback.data
    
    # 解析 postback data
    params = dict(param.split('=') for param in data.split('&'))
    
    if params.get('action') == 'scenario':
        # 快速情境
        scenario = params.get('scenario')
        
        # 使用預設範例快速回應
        examples = reply_generator.generate_quick_scenario_reply(scenario)
        
        # 建立選項
        options = []
        styles = ['formal', 'balanced', 'casual']
        emojis = ['👔', '🤝', '😊']
        titles = ['正式版', '平衡版', '輕鬆版']
        
        for i, example in enumerate(examples[:3]):
            options.append({
                'style': styles[i],
                'emoji': emojis[i],
                'title': f'選項{i+1}：{titles[i]}',
                'text': example
            })
        
        # 建立 Flex Message
        flex_message = flex_builder.create_reply_options_carousel(options)
        line_bot_api.reply_message(event.reply_token, flex_message)
    
    elif params.get('action') == 'adjust_tone':
        # 調整語氣
        original_text = session_manager.get_last_text(user_id)
        if not original_text:
            # 從 data 中取得部分文字
            original_text = params.get('text', '')
        
        # 顯示語氣調整選單
        flex_message = flex_builder.create_tone_adjustment_menu(original_text)
        line_bot_api.reply_message(event.reply_token, flex_message)
    
    elif params.get('tone'):
        # 執行語氣調整
        tone = params.get('tone')
        text = params.get('text', '')
        
        # 取得完整文字（如果被截斷）
        full_text = session_manager.get_last_text(user_id) or text
        
        # 調整語氣
        adjusted_text = reply_generator.adjust_tone(full_text, tone)
        
        # 建立簡單卡片
        tone_labels = {
            'formal': '正式版',
            'casual': '輕鬆版',
            'polite': '委婉版',
            'direct': '直接版'
        }
        
        flex_message = flex_builder.create_simple_reply_card(
            adjusted_text, 
            f"調整後 - {tone_labels.get(tone, '調整版')}"
        )
        
        line_bot_api.reply_message(event.reply_token, flex_message)

def _extract_context_from_message(message):
    """從自然語言中提取情境資訊"""
    context_data = {
        'medium': 'LINE',  # 預設
        'culture': '一般'
    }
    
    # 判斷對象
    if any(word in message for word in ['老闆', '主管', '經理', 'boss']):
        context_data['target_identity'] = '主管'
        context_data['user_identity'] = '員工'
    elif any(word in message for word in ['同事', '同仁', '小王', '小李']):
        context_data['target_identity'] = '同事'
        context_data['user_identity'] = '同事'
    elif any(word in message for word in ['客戶', '客人', '廠商']):
        context_data['target_identity'] = '客戶'
        context_data['user_identity'] = '業務/客服'
    else:
        context_data['target_identity'] = '對方'
        context_data['user_identity'] = '我'
    
    # 判斷情境
    if any(word in message for word in ['請假', '休假', '請病假', '請事假']):
        context_data['context'] = '請假'
    elif any(word in message for word in ['拒絕', '婉拒', '不想', '不要']):
        context_data['context'] = '婉拒邀請或要求'
    elif any(word in message for word in ['催', '提醒', '進度', '期限']):
        context_data['context'] = '催促進度'
    elif any(word in message for word in ['道歉', '抱歉', '對不起', '失誤']):
        context_data['context'] = '道歉'
    elif any(word in message for word in ['感謝', '謝謝', '感恩']):
        context_data['context'] = '表達感謝'
    else:
        # 使用原始訊息作為情境
        context_data['context'] = message
    
    # 判斷媒介
    if any(word in message for word in ['email', 'mail', '郵件', '信件']):
        context_data['medium'] = 'Email'
    elif any(word in message for word in ['電話', '打給', 'call']):
        context_data['medium'] = '電話'
    elif any(word in message for word in ['面對面', '當面', '見面']):
        context_data['medium'] = '面對面'
    
    return context_data

if __name__ == "__main__":
    app.run(debug=False, port=5000)