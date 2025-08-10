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
        prompt_template = ChatPromptTemplate.from_template("""
        你是一個專業的對話顧問。請根據以下資訊生成適當的對話內容：
        
        說話者身份：{user_identity}
        對話對象：{target_identity}
        對話情境：{context}
        過去對話紀錄：{past_conversation}
        
        請生成一段自然、得體且符合情境的對話內容。對話應該：
        1. 符合說話者的身份和語氣
        2. 適合對話對象的身份
        3. 貼合當前的對話情境
        4. 如果有過去對話，要保持一致性
        
        生成的對話：
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
        return result.content.strip()
    
    def polish_conversation(self, session_data, draft, user_id=None):
        prompt_template = ChatPromptTemplate.from_template("""
        你是一個專業的對話顧問。請根據以下資訊優化對話草稿：
        
        說話者身份：{user_identity}
        對話對象：{target_identity}
        對話情境：{context}
        過去對話紀錄：{past_conversation}
        
        使用者的對話草稿：
        {draft}
        
        請優化這段對話，使其：
        1. 更符合說話者的身份和語氣
        2. 更適合對話對象的身份
        3. 更貼合當前的對話情境
        4. 語言更自然流暢
        5. 如果有過去對話，保持風格一致
        
        優化後的對話：
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
        if not last_prompt:
            return "沒有找到之前的對話記錄"
        
        if 'draft' in last_prompt:
            prompt_template = ChatPromptTemplate.from_template("""
            你是一個專業的對話顧問。之前你已經幫助優化了一段對話。
            現在請根據相同的資訊，提供另一個版本的優化對話：
            
            說話者身份：{user_identity}
            對話對象：{target_identity}
            對話情境：{context}
            過去對話紀錄：{past_conversation}
            
            原始草稿：{draft}
            
            請提供一個不同風格但同樣得體的對話版本：
            """)
        else:
            prompt_template = ChatPromptTemplate.from_template("""
            你是一個專業的對話顧問。之前你已經生成了一段對話。
            現在請根據相同的資訊，生成另一個版本的對話：
            
            說話者身份：{user_identity}
            對話對象：{target_identity}
            對話情境：{context}
            過去對話紀錄：{past_conversation}
            
            請生成一段不同但同樣合適的對話內容：
            """)
        
        chain = prompt_template | self.llm
        result = chain.invoke(last_prompt)
        return result.content.strip()