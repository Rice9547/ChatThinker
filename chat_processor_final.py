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
        
        # 分析過去對話，找出需要回應的重點
        past_conv = session_data.get('past_conversation', '無')
        
        # 如果有過去對話，特別強調要回應對方的問題
        if past_conv != '無' and '？' in past_conv:
            context_instruction = """
            特別注意：對方提出了問題，你的回覆必須直接回答這個問題。
            從過去對話中找出對方的疑問，並在回覆中給予具體答案。
            """
        else:
            context_instruction = ""
        
        prompt_template = ChatPromptTemplate.from_template("""
        你是一個台灣對話專家。請根據以下資訊，生成3個可以直接複製使用的回覆訊息。

        情境資訊：
        - 我的身份：{user_identity}
        - 對話對象：{target_identity}  
        - 對話情境：{context}
        - 過去對話：{past_conversation}

        {context_instruction}

        重要要求：
        1. 只提供可以直接傳送的訊息內容
        2. 不要包含任何標籤或說明文字
        3. 使用繁體中文與台灣用語
        4. 如果對方有提問，必須具體回答
        5. 符合身份與情境的語氣

        請提供3個不同風格的回覆：

        ✅ 版本1【正式專業】
        （提供一個正式但友善的回覆，適合維持專業形象）

        ✅ 版本2【平衡友善】  
        （提供一個平衡專業與親切的回覆）

        ✅ 版本3【輕鬆親切】
        （提供一個較輕鬆但仍然得體的回覆）

        記住：每個版本都要能直接複製貼上使用！
        """)
        
        chain = prompt_template | self.llm
        
        last_prompt = {
            'user_identity': session_data.get('user_identity', ''),
            'target_identity': session_data.get('target_identity', ''),
            'context': session_data.get('context', ''),
            'past_conversation': session_data.get('past_conversation', '無'),
            'context_instruction': context_instruction
        }
        
        if self.session_manager and user_id:
            self.session_manager.save_last_prompt(user_id, last_prompt)
        
        result = chain.invoke(last_prompt)
        
        # 格式化輸出，加上分隔線讓用戶更容易複製
        content = result.content.strip()
        
        # 加入使用提示
        formatted_output = "📝 以下是3個回覆選項，請選擇適合的複製使用：\n\n"
        formatted_output += "=" * 40 + "\n"
        formatted_output += content
        formatted_output += "\n" + "=" * 40
        formatted_output += "\n\n💡 小提示：直接長按訊息即可複製\n輸入 /more 可獲得更多版本"
        
        return formatted_output
    
    def polish_conversation(self, session_data, draft, user_id=None):
        """優化使用者提供的草稿"""
        
        prompt_template = ChatPromptTemplate.from_template("""
        你是一個台灣對話專家。請優化以下草稿，提供3個改進版本。

        情境資訊：
        - 我的身份：{user_identity}
        - 對話對象：{target_identity}
        - 對話情境：{context}
        - 過去對話：{past_conversation}

        使用者的草稿：
        「{draft}」

        請提供3個優化版本，每個都要能直接使用：

        ✅ 版本1【正式專業】
        （保持專業但加入適當的友善感）

        ✅ 版本2【平衡友善】
        （平衡專業與親切，最安全的選擇）

        ✅ 版本3【輕鬆親切】
        （較口語但仍保持禮貌）

        優化重點：
        - 保留原意但改善表達
        - 更自然的台灣用語
        - 適當的語氣調整
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
        
        formatted_output = "✨ 以下是優化後的3個版本：\n\n"
        formatted_output += "=" * 40 + "\n"
        formatted_output += result.content.strip()
        formatted_output += "\n" + "=" * 40
        formatted_output += "\n\n💡 小提示：直接長按訊息即可複製"
        
        return formatted_output
    
    def generate_more(self, last_prompt):
        """生成更多版本"""
        if not last_prompt:
            return "沒有找到之前的對話記錄"
        
        # 根據是否有草稿決定提示詞
        if 'draft' in last_prompt:
            task_description = "優化草稿"
        else:
            task_description = "回覆對話"
        
        prompt_template = ChatPromptTemplate.from_template("""
        請根據相同資訊，再提供3個不同風格的{task_description}版本。

        情境資訊：
        - 我的身份：{user_identity}
        - 對話對象：{target_identity}
        - 對話情境：{context}
        - 過去對話：{past_conversation}

        這次請嘗試不同的角度：

        ✅ 版本4【更委婉】
        （用更婉轉的方式表達）

        ✅ 版本5【更積極】
        （展現更多信心與熱情）

        ✅ 版本6【更詳細】
        （提供更多具體資訊）

        每個版本都要能直接複製使用！
        """)
        
        last_prompt['task_description'] = task_description
        
        chain = prompt_template | self.llm
        result = chain.invoke(last_prompt)
        
        formatted_output = "🔄 更多回覆選項：\n\n"
        formatted_output += "=" * 40 + "\n"
        formatted_output += result.content.strip()
        formatted_output += "\n" + "=" * 40
        formatted_output += "\n\n💡 還需要更多？再輸入 /more"
        
        return formatted_output