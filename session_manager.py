import os
import json
import redis
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class SessionManager:
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.session_ttl = 3600 * 24  # 24 hours
    
    def _get_session_key(self, user_id):
        return f"session:{user_id}"
    
    def _get_prompt_key(self, user_id):
        return f"prompt:{user_id}"
    
    def get_session_data(self, user_id):
        key = self._get_session_key(user_id)
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return {}
    
    def set_session_data(self, user_id, data):
        key = self._get_session_key(user_id)
        self.redis_client.setex(key, self.session_ttl, json.dumps(data))
    
    def get_state(self, user_id):
        data = self.get_session_data(user_id)
        return data.get('state')
    
    def set_state(self, user_id, state):
        data = self.get_session_data(user_id)
        data['state'] = state
        self.set_session_data(user_id, data)
    
    def set_user_identity(self, user_id, identity):
        data = self.get_session_data(user_id)
        data['user_identity'] = identity
        self.set_session_data(user_id, data)
    
    def set_target_identity(self, user_id, target):
        data = self.get_session_data(user_id)
        data['target_identity'] = target
        self.set_session_data(user_id, data)
    
    def set_context(self, user_id, context):
        data = self.get_session_data(user_id)
        data['context'] = context
        self.set_session_data(user_id, data)
    
    def set_past_conversation(self, user_id, conversation):
        data = self.get_session_data(user_id)
        data['past_conversation'] = conversation
        self.set_session_data(user_id, data)
    
    def clear_session(self, user_id):
        session_key = self._get_session_key(user_id)
        prompt_key = self._get_prompt_key(user_id)
        self.redis_client.delete(session_key)
        self.redis_client.delete(prompt_key)
    
    def save_last_prompt(self, user_id, prompt):
        key = self._get_prompt_key(user_id)
        self.redis_client.setex(key, self.session_ttl, json.dumps(prompt))
    
    def get_last_prompt(self, user_id):
        key = self._get_prompt_key(user_id)
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None