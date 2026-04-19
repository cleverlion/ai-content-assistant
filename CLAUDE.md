# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 FastAPI 的 Python Web 服务项目，提供了基础的 CORS 配置和 RESTful API 接口。

## 项目结构

```
.
├── main.py              # 主应用程序文件
├── login.html           # 登录页面（静态文件）
└── .venv/               # Python 虚拟环境
```

## 常用命令

### 启动开发服务器
```bash
# 使用 uvicorn 启动服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或指定特定端口
uvicorn main:app --reload --port 8080
```

### 安装依赖
```bash
# 激活虚拟环境
source .venv/Scripts/activate  # Linux/Mac
# 或
.venv\Scripts\activate         # Windows

# 安装 FastAPI 和 uvicorn
pip install fastapi uvicorn

# 安装 CORS 中间件（通常已包含在 fastapi 中）
pip install fastapi-cors
```

### API 测试
```bash
# 使用 curl 测试 API
curl http://localhost:8000/
curl http://localhost:8000/health

# 或访问自动生成的文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 代码架构

### 主要组件
1. **FastAPI 应用** (`main.py:4`) - 创建 FastAPI 实例
2. **CORS 中间件** (`main.py:14-20`) - 配置跨域资源共享
3. **路由处理** - 定义 API 端点

### 已定义接口
- `GET /` - 根路径，返回欢迎信息
- `GET /health` - 健康检查接口

## 开发指南

### 添加新接口
在 `main.py` 中使用装饰器定义新路由：
```python
@app.get("/new-endpoint")
async def new_endpoint():
    return {"message": "New endpoint"}
```

### 配置 CORS
修改 `origins` 列表添加允许的域名：
```python
origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://your-domain.com",  # 添加您的域名
]
```

### 运行静态文件服务
如果需要提供静态文件（如 login.html）：
```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="."), name="static")
# 然后通过 http://localhost:8000/static/login.html 访问
```

## 依赖说明
- **fastapi** - Web 框架
- **uvicorn** - ASGI 服务器
- **fastapi-cors** - CORS 中间件支持

## 环境要求
- Python 3.7+
- FastAPI
- Uvicorn