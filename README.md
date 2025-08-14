# Geo-Agent
Geo-Agent 是一款对话式地图可视化平台，用户可通过自然语言与 AI 交互，系统基于语义理解自动解析意图、获取数据，联动地图进行可视化展示，实现"开口即可见"的智能空间信息服务。

## 🚀 项目架构

```
geo-agent/
├── app/                    # 应用主目录
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── api/               # API层
│   │   ├── __init__.py
│   │   └── websocket.py   # WebSocket API (专注于地图联动)
│   ├── core/              # 核心模块
│   │   ├── __init__.py
│   │   ├── ai_engine.py   # 多模型AI意图解析引擎
│   │   └── plugin_manager.py # 插件管理器
│   ├── models/            # 数据模型
│   │   ├── __init__.py
│   │   └── message.py     # 消息数据模型
│   ├── plugins/           # 插件模块
│   │   ├── __init__.py
│   │   ├── weather_plugin.py # 天气查询插件
│   │   └── poi_plugin.py  # POI搜索插件
│   ├── services/          # 服务层
│   │   ├── __init__.py
│   │   ├── chat_service.py # 聊天服务 (意图解析和地图联动)
│   │   └── dialog_service.py # 对话服务 (直接调用Qwen API)
│   └── utils/             # 工具模块
│       ├── __init__.py
│       └── logger.py      # 日志工具
├── static/                # 静态文件
│   └── test_chat.html     # 测试页面
├── main.py                # 应用入口
├── requirements.txt       # 依赖包
├── env.example           # 环境变量示例
├── test_framework.py     # 框架测试脚本
├── test_qwen.py          # Qwen-Flash测试脚本
├── test_qwen_new.py      # Qwen OpenAI兼容模式测试脚本
├── test_separated.py     # 分离功能测试脚本
├── start.py              # 启动脚本
├── .gitignore           # Git忽略文件
└── README.md            # 项目说明
```

## 🛠️ 技术栈

- **后端框架**: FastAPI + WebSocket
- **AI集成**: 支持OpenAI和Qwen-Flash模型
- **对话功能**: 直接调用Qwen API进行流式对话（OpenAI兼容模式）
- **地图联动**: WebSocket实时传递地图操作指令
- **插件系统**: 可扩展的插件架构
- **日志系统**: Loguru
- **配置管理**: Pydantic Settings

## 🏗️ 架构设计

### 功能分离设计

1. **对话功能** (`app/services/dialog_service.py`)
   - 直接调用Qwen API进行流式对话（使用OpenAI兼容模式）
   - 支持简单对话和流式对话
   - 独立于WebSocket，可单独使用

2. **地图联动功能** (`app/api/websocket.py`)
   - 专注于意图识别后的地图操作
   - 通过WebSocket向前端传递JSON指令
   - 支持地图飞行、标记添加等操作

3. **意图解析** (`app/core/ai_engine.py`)
   - 解析用户自然语言意图
   - 提取关键参数（地点、类型等）
   - 为地图联动提供结构化数据

### 工作流程

```
用户输入自然语言
    ↓
1. 对话功能: 直接调用Qwen API → 流式回复
    ↓
2. 意图解析: AI引擎解析意图 → 结构化数据
    ↓
3. 插件执行: 调用相应插件 → 获取数据
    ↓
4. 地图联动: WebSocket传递指令 → 前端地图操作
```

## 🤖 AI模型支持

### OpenAI模型
- 支持GPT-4、GPT-3.5等模型
- 配置`AI_PROVIDER=openai`
- 需要配置`OPENAI_API_KEY`

### Qwen-Flash模型
- 阿里云通义千问模型
- 使用OpenAI兼容模式API调用
- 配置`AI_PROVIDER=qwen`
- 需要配置`QWEN_API_KEY`
- 推荐使用，响应速度快，成本低

## 📦 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑 .env 文件，选择AI提供商并配置API Key

# 使用Qwen-Flash模型（推荐）
AI_PROVIDER=qwen
QWEN_API_KEY=your_qwen_api_key_here

# 或使用OpenAI模型
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 测试功能

```bash
# 测试Qwen OpenAI兼容模式
python test_qwen_new.py

# 测试对话功能
python test_separated.py dialog

# 测试WebSocket地图联动
python test_separated.py websocket

# 测试意图解析
python test_separated.py intent

# 运行所有测试
python test_separated.py
```

### 4. 启动服务

```bash
# 启动开发服务器
python main.py

# 或者使用启动脚本
python start.py

# 或者使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 访问服务

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **插件状态**: http://localhost:8000/plugins
- **WebSocket**: ws://localhost:8000/ws
- **测试页面**: http://localhost:8000/static/test_chat.html

## 💬 对话功能使用

### 直接调用对话服务

```python
from app.services.dialog_service import dialog_service

# 简单对话
response = await dialog_service.chat_simple("你好，请介绍一下你自己")
print(response)

# 流式对话
async for chunk in dialog_service.chat_stream("什么是地理信息系统？"):
    print(chunk, end="", flush=True)
```

### 对话功能特点

- **OpenAI兼容模式**: 使用标准的OpenAI SDK调用Qwen API
- **直接API调用**: 不依赖WebSocket，响应更快
- **流式输出**: 支持实时流式对话
- **独立服务**: 可单独使用，易于集成
- **错误处理**: 完善的异常处理机制

### Qwen API调用方式

项目使用Qwen的OpenAI兼容模式，通过以下方式调用：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_qwen_api_key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 流式对话
completion = client.chat.completions.create(
    model="qwen-flash",
    messages=[
        {"role": "system", "content": "你是一个友好的地理信息助手。"},
        {"role": "user", "content": "你好"}
    ],
    stream=True
)

for chunk in completion:
    if chunk.choices:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
```

## 🗺️ WebSocket地图联动

### 连接WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/your-session-id');
```

### 发送消息

```javascript
ws.send(JSON.stringify({
    "type": "user_input",
    "message": "我想看看北京的天气"
}));
```

### 接收地图指令

```javascript
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'intent_parsed':
            console.log('意图解析结果:', data.intent);
            break;
        case 'plugin_result':
            console.log('插件执行结果:', data.data);
            break;
        case 'map_action':
            console.log('地图操作指令:', data.action);
            // 执行地图操作
            executeMapAction(data.action, data.parameters);
            break;
    }
};
```

### 地图操作类型

- **fly_to_location**: 飞行到指定位置
- **add_poi_markers**: 添加POI标记点
- **add_path**: 添加路径
- **clear_markers**: 清除标记

## 🔌 插件系统

项目采用插件化架构，支持以下插件类型：

- **天气查询** (`QWEATHER`): 查询指定地区的天气信息
- **POI搜索** (`BAIDU_MAP`): 搜索兴趣点信息
- **路径规划** (待实现): 计算两点间的路径
- **地理编码** (待实现): 地址与坐标转换

### 添加新插件

1. 在 `app/plugins/` 目录下创建新的插件文件
2. 继承 `BasePlugin` 类并实现必要的方法
3. 在插件文件中添加注册函数
4. 在 `ChatService` 中导入并注册插件

## 🎯 核心功能

### 1. 自然语言理解
- 支持多种AI模型（OpenAI、Qwen-Flash）
- 智能意图解析和参数提取
- 高置信度响应处理

### 2. 对话功能
- 使用Qwen OpenAI兼容模式，调用简单
- 直接调用Qwen API，响应速度快
- 支持流式输出，用户体验好
- 独立服务，易于集成

### 3. 地图联动
- WebSocket实时传递地图指令
- 支持多种地图操作
- 与前端Cesium地图完美集成

### 4. 插件调度
- 根据意图自动选择插件
- 插件执行结果格式化
- 错误处理和重试机制

## 🔧 开发指南

### 项目结构说明

- **`app/core/`**: 核心业务逻辑
  - `ai_engine.py`: 多模型AI意图解析引擎
  - `plugin_manager.py`: 插件管理系统

- **`app/services/`**: 服务层
  - `chat_service.py`: 聊天服务，处理意图解析和地图联动
  - `dialog_service.py`: 对话服务，直接调用Qwen API

- **`app/plugins/`**: 插件实现
  - 每个插件都是独立的模块
  - 遵循统一的接口规范

- **`app/api/`**: API接口层
  - `websocket.py`: WebSocket连接管理（专注于地图联动）

### 添加新功能

1. **新意图类型**: 在 `app/models/message.py` 中添加新的 `IntentType`
2. **新插件**: 在 `app/plugins/` 中创建新插件
3. **新服务**: 在 `app/services/` 中添加业务逻辑
4. **新AI模型**: 在 `app/core/ai_engine.py` 中添加新的提供商类

## 🚧 待实现功能

- [ ] 地理编码插件
- [ ] 路径规划插件
- [ ] 实时交通信息
- [ ] 语音输入支持
- [ ] 前端Vue3 + Cesium界面
- [ ] 用户会话管理
- [ ] 插件热加载
- [ ] 性能监控

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**Geo-Agent** - 让地图交互更智能！

