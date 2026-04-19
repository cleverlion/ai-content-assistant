# ==================== 导入模块 ====================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os
from dotenv import load_dotenv

# LangChain 相关导入
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage

# ==================== 加载环境变量 ====================
load_dotenv()  # 自动读取 .env 文件中的 DASHSCOPE_API_KEY

# ==================== 创建 FastAPI 应用 ====================
app = FastAPI()

# 配置 CORS（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Pydantic 数据模型 ====================
class ContentRequest(BaseModel):
    """前端发送的请求体格式"""
    topic: str
    style: str = "专业"

class ContentResponse(BaseModel):
    """后端返回的响应体格式"""
    status: str
    idea: str
    processing_time: float

# ==================== API 路由 ====================
@app.get("/")
async def root():
    return {"message": "Hello AI Agent! 你的全栈之路开始了！"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """
    核心接口：接收前端传来的主题和风格，调用大模型生成创意文案。
    """
    # ---- 1. 记录开始时间（用于计算耗时） ----
    start_time = time.time()

    # ---- 2. 初始化大模型（使用阿里云百炼的通义千问） ----
    #     temperature=0.7 表示适中的创造性，可根据需要调整
    llm = ChatTongyi(model="qwen-turbo", temperature=0)

    # ---- 3. 构造提示词（Messages） ----
    #     SystemMessage：给 AI 设定角色和任务
    system_prompt = (
        "你是一个专业的内容营销AI助理。"
        "请根据用户提供的主题和风格，生成一个富有创意、可直接执行的内容点子。"
        "只需返回点子本身，不需要额外解释。"
    )
    #     HumanMessage：将前端传来的数据嵌入到提示中
    human_prompt = f"主题：{request.topic}，风格：{request.style}"

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]

    # ---- 4. 调用大模型，获取 AI 生成的创意 ----
    try:
        ai_response = llm.invoke(messages)
        idea = ai_response.content
        status = "success"
    except Exception as e:
        # 如果调用失败，返回友好的错误信息
        idea = f"AI 服务暂时不可用，请稍后重试。错误详情：{str(e)}"
        status = "error"

    # ---- 5. 计算处理耗时 ----
    elapsed_time = round(time.time() - start_time, 3)

    # ---- 6. 返回结构化响应 ----
    return ContentResponse(
        status=status,
        idea=idea,
        processing_time=elapsed_time
    )