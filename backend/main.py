# ==================== 导入模块 ====================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os
from dotenv import load_dotenv
import operator
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END

# LangChain 相关导入
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient

# ==================== 加载环境变量 ====================
load_dotenv()  # 自动读取 .env 文件中的 DASHSCOPE_API_KEY

# ==================== 模型配置（方便全局切换） ====================
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen-turbo")

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

class AgentState(TypedDict):
    topic: str
    style: str
    research_material: str
    draft: str
    final_content: str
    # messages: Annotated[List[str], operator.add] # 可选，用于记录详细日志

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


# ==================== 定义 LangGraph 工作流 ====================
# 1. 定义节点函数
# 研究员 Agent
def researcher_node(state: AgentState) -> AgentState:
    print(f"--- [研究员] 开始研究主题: {state['topic']} ---")
    # 调用 Tavily 搜索相关资料（示例，实际使用时根据需要调整）
    search_result = None
    retry_count = 0
    # 实例化 Tavily 客户端（如果需要使用 Tavily 的功能，可以在节点函数中调用）
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    while retry_count < 2:
        try:
            search_result = tavily.search(query=state['topic'], max_results=3, include_raw_content=False)
            break
        except:
            retry_count += 1
            if retry_count >= 2:
                search_result = {'results': []}
                break
    # 如果搜索失败，使用大模型知识生成研究材料
    if not search_result.get('results'):
        search_result = {
            'results': [
                {
                    'title': '默认知识库条目',
                    'content': '由于外部搜索失败，此处使用大模型内置知识进行补充。\n1. 研究主题：{state["topic"]}\n2. 专业风格：{state["style"]}\n3. 内容框架：引言 -> 核心观点 -> 结论\n4. 关键词优化：[自动生成]'
                }
            ]
        }
  # 将搜索结果整理成文本摘要
    research_material = f"搜索主题「{state['topic']}」的相关信息：\n"
    for idx, result in enumerate(search_result.get("results", []), 1):
        research_material += f"{idx}. {result['title']}\n   {result['content']}\n"
    
    print(f"--- [研究员] 搜索完成，获得 {len(search_result.get('results', []))} 条结果 ---")
    return {"research_material": research_material}

# 撰稿人 Agent
def writer_node(state: AgentState) -> AgentState:
    print(f"--- [撰稿人] 开始创作，风格: {state['style']} ---")
    llm = ChatTongyi(model=DEFAULT_MODEL, temperature=0.7) # 撰稿可提高创造性
    system_prompt = f"你是一个内容营销撰稿人。请根据研究材料和指定风格（{state['style']}），撰写一篇吸引人的短文初稿。"
    human_prompt = f"研究材料：\n{state['research_material']}\n\n请开始创作："
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
    response = llm.invoke(messages)
    return {"draft": response.content}

# 编辑 Agent
def editor_node(state: AgentState) -> AgentState:
    print(f"--- [编辑] 正在审校和润色 ---")
    llm = ChatTongyi(model=DEFAULT_MODEL, temperature=0.7) # 编辑需要更严谨
    system_prompt = "你是一个资深内容编辑。请审校下面的初稿，进行润色和优化，使其更具可读性和吸引力，但不要改变原意。直接返回优化后的最终文案。"
    human_prompt = f"初稿内容：\n{state['draft']}"
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]
    response = llm.invoke(messages)
    return {"final_content": response.content}

# 2. 构建 LangGraph 工作流
def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("editor", editor_node)

    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "editor")
    workflow.add_edge("editor", END)

    return workflow.compile()

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
    # 编译并运行工作流图
    try:
        # 编译并运行工作流图
        graph_app = build_graph()
        initial_state = {"topic": request.topic, "style": request.style}
        final_state = graph_app.invoke(initial_state)
        status = "success"
        idea = final_state["final_content"]
    except Exception as e:
        status = "error"
        idea = f"工作流执行失败，错误详情：{str(e)}"
    elapsed_time = round(time.time() - start_time, 3)
    return ContentResponse(status=status, idea=idea, processing_time=elapsed_time)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)