# 聊天優化機器人

一個 line bot 的 webhook server，希望用 python 實現，功能是：
1. 請 user 輸入他是誰、對象是誰、說話情境、過去對話紀錄（應該會分階段請 user 輸入），然後問 user 是希望直接產對話還是請他給你對話幫忙潤飾
2. 串 langchain，用 openai api 根據 user 的 input 產出建議內容
3. 若 user 打 /more 是同個 prompt 產更多內容
4. 也許可以用 /new 當作是新的對話