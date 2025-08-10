import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class ChatProcessor:
    def __init__(self, session_manager=None):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-3.5-turbo",
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.session_manager = session_manager
    
    def generate_conversation(self, session_data, user_id=None):
        """生成3個可直接使用的回覆選項"""
        
        prompt_template = ChatPromptTemplate.from_template("""
        你是一個台灣對話專家。請根據以下資訊，生成3個可以直接複製使用的回覆文字。

        情境資訊：
        - 我的身份：{user_identity}
        - 對話對象：{target_identity}  
        - 對話情境：{context}
        - 過去對話：{past_conversation}

        重要要求：
        1. 只提供回覆文字，不要對話過程
        2. 每個選項都是完整、可直接使用的訊息
        3. 不要包含「我：」或任何標籤
        4. 使用繁體中文，符合台灣用語
        5. 根據情境調整語氣（正式/輕鬆）

        請提供3個版本：

        【版本1-正式禮貌】
        [提供一個正式但友善的回覆，適合維持專業關係]

        【版本2-中等友善】  
        [提供一個平衡專業與親切的回覆]

        【版本3-輕鬆直接】
        [提供一個較輕鬆但仍然得體的回覆]
        """)
        
        chain = prompt_template | self.llm
        
        last_prompt = {
            'user_identity': session_data.get('user_identity', ''),
            'target_identity': session_data.get('target_identity', ''),
            'context': session_data.get('context', ''),
            'past_conversation': session_data.get('past_conversation', '無')
        }
        
        if self.session_manager and user_id:
            self.session_manager.save_last_prompt(user_id, last_prompt)
        
        result = chain.invoke(last_prompt)
        
        # 格式化輸出
        content = result.content.strip()
        
        # 確保輸出格式正確
        if "【版本1" not in content:
            # 如果格式不對，重新整理
            lines = content.split('\n')
            formatted = "以下是3個回覆選項，請選擇最適合的使用：\n\n"
            formatted += "【版本1-正式禮貌】\n"
            formatted += lines[0] if len(lines) > 0 else "（生成失敗）"
            formatted += "\n\n【版本2-中等友善】\n"
            formatted += lines[1] if len(lines) > 1 else "（生成失敗）"
            formatted += "\n\n【版本3-輕鬆直接】\n"
            formatted += lines[2] if len(lines) > 2 else "（生成失敗）"
            return formatted
        
        return content
    
    def polish_conversation(self, session_data, draft, user_id=None):
        """優化使用者提供的草稿，提供3個版本"""
        
        prompt_template = ChatPromptTemplate.from_template("""
        你是一個台灣對話專家。請優化以下草稿，提供3個不同風格的版本。

        情境資訊：
        - 我的身份：{user_identity}
        - 對話對象：{target_identity}
        - 對話情境：{context}
        - 過去對話：{past_conversation}

        使用者的草稿：
        {draft}

        請提供3個優化版本：

        【版本1-正式禮貌】
        [保持專業但友善的語氣]

        【版本2-中等友善】
        [平衡專業與親切感]

        【版本3-輕鬆直接】
        [較口語但仍得體]

        注意：
        - 保留原意但改善表達
        - 符合台灣用語習慣
        - 每個版本都可直接使用
        """)
        
        chain = prompt_template | self.llm
        
        last_prompt = {
            'user_identity': session_data.get('user_identity', ''),
            'target_identity': session_data.get('target_identity', ''),
            'context': session_data.get('context', ''),
            'past_conversation': session_data.get('past_conversation', '無'),
            'draft': draft
        }
        
        if self.session_manager and user_id:
            self.session_manager.save_last_prompt(user_id, last_prompt)
        
        result = chain.invoke(last_prompt)
        return result.content.strip()
    
    def generate_more(self, last_prompt):
        """生成更多版本"""
        if not last_prompt:
            return "沒有找到之前的對話記錄"
        
        prompt_template = ChatPromptTemplate.from_template("""
        請根據相同資訊，再提供3個不同的回覆版本。

        這次請嘗試不同的角度：
        1. 更委婉的版本
        2. 更積極的版本  
        3. 加入更多細節的版本

        情境資訊：
        - 我的身份：{user_identity}
        - 對話對象：{target_identity}
        - 對話情境：{context}
        - 過去對話：{past_conversation}

        請提供3個新版本：

        【版本4-委婉版】
        [更加婉轉的表達方式]

        【版本5-積極版】
        [更有信心和說服力]

        【版本6-詳細版】
        [包含更多具體說明]
        """)
        
        chain = prompt_template | self.llm
        result = chain.invoke(last_prompt)
        return result.content.strip()