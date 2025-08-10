import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class ReplyGenerator:
    """直接生成可用回覆文字的處理器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-3.5-turbo",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
    
    def generate_reply_options(self, context_data):
        """生成3個不同風格的回覆選項"""
        
        prompt_template = ChatPromptTemplate.from_template("""
        你是回覆建議助手。請根據用戶情境，直接提供3個可以複製使用的回覆文字。

        情境資訊：
        - 身份：{user_identity}
        - 對象：{target_identity}
        - 情境：{context}
        - 溝通方式：{medium}
        - 公司文化：{culture}

        輸出格式要求：
        1. 只提供回覆文字，不要對話過程
        2. 每個選項都是完整、可直接使用的訊息
        3. 不要包含"我："或說話者標籤
        4. 根據溝通方式調整（LINE可用表情、Email要完整）

        請提供3個選項：

        【選項1-正式委婉】
        [提供30-80字的完整回覆，適合正式場合]

        【選項2-平衡適中】
        [提供30-80字的完整回覆，兼顧禮貌與親和]

        【選項3-輕鬆直接】
        [提供30-80字的完整回覆，較口語化{emoji_hint}]

        注意：
        - 使用繁體中文
        - 符合台灣用語習慣
        - 每個選項都要能直接複製使用
        """)
        
        # 根據媒介決定是否使用表情
        emoji_hint = "，可適度使用表情符號" if context_data.get('medium') == 'LINE' else ""
        
        chain = prompt_template | self.llm
        
        params = {
            'user_identity': context_data.get('user_identity', '一般員工'),
            'target_identity': context_data.get('target_identity', '主管'),
            'context': context_data.get('context', ''),
            'medium': context_data.get('medium', 'LINE'),
            'culture': context_data.get('culture', '一般'),
            'emoji_hint': emoji_hint
        }
        
        result = chain.invoke(params)
        return self._parse_reply_options(result.content)
    
    def _parse_reply_options(self, content):
        """解析生成的回覆選項"""
        options = []
        
        # 分割選項
        sections = content.split('【選項')
        
        for section in sections[1:]:  # 跳過第一個空白部分
            if '】' in section:
                title_end = section.index('】')
                title = section[:title_end]
                text = section[title_end+1:].strip()
                
                # 清理文字
                text = text.replace('[', '').replace(']', '')
                text = text.split('\n')[0].strip()  # 只取第一行
                
                # 判斷風格
                if '正式' in title or '委婉' in title:
                    style = 'formal'
                    emoji = '👔'
                elif '平衡' in title or '適中' in title:
                    style = 'balanced'
                    emoji = '🤝'
                else:
                    style = 'casual'
                    emoji = '😊'
                
                options.append({
                    'style': style,
                    'emoji': emoji,
                    'title': f"選項{len(options)+1}：{title.strip('-')}",
                    'text': text
                })
        
        # 如果解析失敗，返回預設選項
        if not options:
            options = [
                {
                    'style': 'formal',
                    'emoji': '👔',
                    'title': '選項1：正式版',
                    'text': content.strip()[:100]
                }
            ]
        
        return options
    
    def generate_quick_scenario_reply(self, scenario):
        """針對快速情境生成回覆"""
        
        quick_scenarios = {
            "請假": {
                "context": "需要請假",
                "examples": [
                    "老闆早安，明天需要請假一天，家裡有急事要處理",
                    "不好意思，明天想請個假，有些私事需要處理",
                    "老闆，明天有事想請假，會先把工作安排好"
                ]
            },
            "拒絕加班": {
                "context": "婉拒加班要求",
                "examples": [
                    "不好意思，今晚已有安排，明天一早我會優先處理",
                    "抱歉，晚上有事走不開，這個我明天第一件處理可以嗎",
                    "今天真的不行，家裡有事😅 明天我早點來趕"
                ]
            },
            "催進度": {
                "context": "禮貌催促進度",
                "examples": [
                    "請問之前提到的資料準備好了嗎？需要的話我可以協助",
                    "不好意思提醒一下，那份文件今天需要用到，方便了嗎",
                    "Hi，上次說的東西好了嗎？老闆在問😅"
                ]
            },
            "道歉": {
                "context": "工作失誤道歉",
                "examples": [
                    "很抱歉這次的疏失，我會立即修正並避免再次發生",
                    "不好意思，是我的失誤，馬上處理，以後會更注意",
                    "抱歉抱歉，我的錯💦 現在就改"
                ]
            }
        }
        
        if scenario in quick_scenarios:
            return quick_scenarios[scenario]["examples"]
        else:
            # 使用 AI 生成
            context_data = {
                'context': scenario,
                'medium': 'LINE',
                'culture': '一般'
            }
            options = self.generate_reply_options(context_data)
            return [opt['text'] for opt in options]
    
    def adjust_tone(self, original_text, new_tone):
        """調整既有文字的語氣"""
        
        prompt_template = ChatPromptTemplate.from_template("""
        請將以下文字調整為{tone}的語氣，保持原意但改變表達方式：

        原文：{original}

        語氣說明：
        - 更正式：使用敬語、完整句子、避免口語
        - 更輕鬆：加入口語、適度表情符號、親切感
        - 更委婉：間接表達、給對方台階、柔和用詞
        - 更直接：簡潔明瞭、直說重點、減少修飾

        調整後（繁體中文）：
        """)
        
        tone_map = {
            'formal': '更正式',
            'casual': '更輕鬆',
            'polite': '更委婉',
            'direct': '更直接'
        }
        
        chain = prompt_template | self.llm
        result = chain.invoke({
            'original': original_text,
            'tone': tone_map.get(new_tone, '更平衡')
        })
        
        return result.content.strip()