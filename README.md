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
│   │   └── websocket.py   # WebSocket API
│   ├── core/              # 核心模块
│   │   ├── __init__.py
│   │   ├── ai_engine.py   # AI意图解析引擎
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
│   │   └── chat_service.py # 聊天服务
│   └── utils/             # 工具模块
│       ├── __init__.py
│       └── logger.py      # 日志工具
├── main.py                # 应用入口
├── requirements.txt       # 依赖包
├── env.example           # 环境变量示例
├── .gitignore           # Git忽略文件
└── README.md            # 项目说明
```

## 🛠️ 技术栈

- **后端框架**: FastAPI + WebSocket
- **AI集成**: OpenAI API
- **插件系统**: 可扩展的插件架构
- **日志系统**: Loguru
- **配置管理**: Pydantic Settings

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

# 编辑 .env 文件，填入你的配置
# 特别是 OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 启动服务

```bash
# 启动开发服务器
python main.py

# 或者使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问服务

- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **插件状态**: http://localhost:8000/plugins
- **WebSocket**: ws://localhost:8000/ws

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

## 📡 WebSocket API

### 连接

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

### 接收消息

```javascript
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
    
    switch(data.type) {
        case 'intent_parsed':
            console.log('意图解析结果:', data.intent);
            break;
        case 'plugin_result':
            console.log('插件执行结果:', data.data);
            break;
        case 'map_action':
            console.log('地图操作指令:', data.action);
            break;
    }
};
```

## 🎯 核心功能

### 1. 自然语言理解
- 基于OpenAI的意图解析
- 支持多种地理信息查询意图
- 参数自动提取和验证

### 2. 插件调度
- 根据意图自动选择插件
- 插件执行结果格式化
- 错误处理和重试机制

### 3. 地图联动
- 生成地图操作指令
- 支持飞行、标记、路径等操作
- 与前端Cesium地图集成

## 🔧 开发指南

### 项目结构说明

- **`app/core/`**: 核心业务逻辑
  - `ai_engine.py`: AI意图解析引擎
  - `plugin_manager.py`: 插件管理系统

- **`app/plugins/`**: 插件实现
  - 每个插件都是独立的模块
  - 遵循统一的接口规范

- **`app/services/`**: 服务层
  - `chat_service.py`: 聊天服务，协调各个组件

- **`app/api/`**: API接口层
  - `websocket.py`: WebSocket连接管理

### 添加新功能

1. **新意图类型**: 在 `app/models/message.py` 中添加新的 `IntentType`
2. **新插件**: 在 `app/plugins/` 中创建新插件
3. **新服务**: 在 `app/services/` 中添加业务逻辑
4. **新API**: 在 `app/api/` 中添加接口

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

