# backend/test_langgraph.py
from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1. 定义状态 (State)
class GraphState(TypedDict):
    input: str
    result: str

# 2. 定义节点 (Node) 函数
def my_node(state: GraphState) -> GraphState:
    """一个简单的节点，将输入文本转为大写"""
    print(f"--- 节点执行: 接收到输入 '{state['input']}' ---")
    return {"result": state["input"].upper()}

# 3. 构建图 (Graph)
workflow = StateGraph(GraphState)
workflow.add_node("uppercase_node", my_node) # 添加节点

# 4. 定义流程 (Edges)
workflow.set_entry_point("uppercase_node")    # 设置入口节点
workflow.add_edge("uppercase_node", END)      # 节点执行后结束

# 5. 编译图 (Compile)
app = workflow.compile()

# 6. 运行图 (Invoke)
initial_state = {"input": "hello langgraph", "result": ""}
final_state = app.invoke(initial_state)

print(f"最终状态: {final_state}")
# 预期输出: 最终状态: {'input': 'hello langgraph', 'result': 'HELLO LANGGRAPH'}