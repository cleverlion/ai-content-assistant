# test_tongyi.py
import os
from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatTongyi(model="qwen-turbo", temperature=0.7)

messages = [
    SystemMessage(content="你是一个专业的全栈AI开发专家。"),
    HumanMessage(content="什么是LangChain？")
]

response = llm.invoke(messages)
print(response.content)