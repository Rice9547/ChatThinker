#!/usr/bin/env python3
"""
測試腳本，檢查所有依賴是否正確安裝
"""

def test_imports():
    """測試所有必要的套件是否能正常導入"""
    try:
        print("Testing Flask...")
        from flask import Flask
        print("✅ Flask OK")
        
        print("Testing LINE Bot SDK...")
        from linebot import LineBotApi, WebhookHandler
        print("✅ LINE Bot SDK OK")
        
        print("Testing LangChain...")
        from langchain_openai import ChatOpenAI
        from langchain.prompts import ChatPromptTemplate
        print("✅ LangChain OK")
        
        print("Testing Redis...")
        import redis
        print("✅ Redis OK")
        
        print("Testing python-dotenv...")
        from dotenv import load_dotenv
        print("✅ python-dotenv OK")
        
        print("Testing OpenAI...")
        import openai
        print("✅ OpenAI OK")
        
        print("\n🎉 All dependencies are installed correctly!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

def test_app_structure():
    """測試應用結構"""
    try:
        print("\nTesting app structure...")
        from app import app, session_manager, chat_processor
        print("✅ Main app components OK")
        
        from session_manager import SessionManager
        print("✅ SessionManager OK")
        
        from chat_processor import ChatProcessor
        print("✅ ChatProcessor OK")
        
        print("✅ App structure OK")
        
    except Exception as e:
        print(f"❌ App structure error: {e}")
        return False
    
    return True

def test_redis_connection():
    """測試 Redis 連接"""
    try:
        print("\nTesting Redis connection...")
        import redis
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            print("✅ Redis connection OK")
            return True
        except redis.ConnectionError:
            print("⚠️  Redis not running or not accessible")
            print("   Please start Redis server: brew services start redis")
            return False
            
    except Exception as e:
        print(f"❌ Redis test error: {e}")
        return False

def main():
    """主測試函數"""
    print("🔍 Testing chatbot setup...\n")
    
    success = True
    success &= test_imports()
    success &= test_app_structure()
    success &= test_redis_connection()
    
    if success:
        print("\n🎯 All tests passed! Your chatbot is ready to run.")
        print("\nNext steps:")
        print("1. Edit .env file with your LINE Bot and OpenAI credentials")
        print("2. Start Redis: brew services start redis")
        print("3. Run the app: python3 run.py")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main()