# 阿里云百炼流式聊天服务使用指南

## 概述

流式聊天服务支持实时流式输出，使用阿里云百炼API进行自然语言对话。

## 配置

### 1. 环境变量配置

在项目根目录创建 `.env` 文件，配置以下环境变量：

```bash
# 阿里云百炼API配置
DASHSCOPE_API_KEY=sk-xxx
DASHSCOPE_MODEL=qwen-plus
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 2. API密钥获取

访问 [阿里云百炼控制台](https://dashscope.console.aliyun.com/) 获取API密钥

## 使用方法

### 1. 基本使用

```python
from app.services.stream_chat_service import StreamChatService

# 初始化服务
chat_service = StreamChatService()

# 流式对话
async for chunk in chat_service.stream_chat("你好，请介绍一下你自己"):
    if chunk["type"] == "stream_chunk":
        print(chunk["chunk"], end="", flush=True)
```

### 2. 完整示例

```python
import asyncio
from app.services.stream_chat_service import StreamChatService

async def chat_example():
    chat_service = StreamChatService()
    
    async for chunk in chat_service.stream_chat("北京今天天气怎么样？"):
        if chunk["type"] == "stream_start":
            print("🚀 开始流式传输...")
        elif chunk["type"] == "stream_chunk":
            print(chunk["chunk"], end="", flush=True)
        elif chunk["type"] == "stream_end":
            print("\n✅ 流式传输完成")
        elif chunk["type"] == "error":
            print(f"\n❌ 错误: {chunk['error']}")

# 运行示例
asyncio.run(chat_example())
```

### 3. 运行示例脚本

```bash
python examples/stream_chat_example.py
```

## 功能特性

### 1. 阿里云百炼API支持

- 使用 `qwen-plus` 等高级模型
- 支持流式输出和实时响应
- 完整的错误处理机制

### 2. 流式输出

- 实时字符级流式输出
- 支持会话管理
- 错误处理和重试机制

### 3. 地理信息助手

内置地理信息助手功能：
- 天气查询
- POI搜索
- 地理建议
- 地图操作

## 响应格式

流式聊天服务返回以下格式的响应：

```json
{
    "type": "stream_start|stream_chunk|stream_end|error",
    "message_id": "uuid",
    "session_id": "uuid",
    "chunk": "文本内容",  // 仅在 stream_chunk 类型时存在
    "error": "错误信息"   // 仅在 error 类型时存在
}
```

## 错误处理

常见错误及解决方案：

1. **API密钥未配置**
   ```
   错误: 阿里云百炼API Key未配置
   解决: 在.env文件中配置DASHSCOPE_API_KEY
   ```

2. **网络连接问题**
   ```
   错误: 网络连接超时
   解决: 检查网络连接和API端点配置
   ```

3. **模型不存在**
   ```
   错误: 模型不存在
   解决: 检查模型名称是否正确
   ```

## 性能优化

1. **并发处理**: 支持多个并发会话
2. **内存管理**: 流式处理减少内存占用
3. **错误恢复**: 自动重试和错误恢复机制

## 注意事项

1. 确保API密钥有足够的配额
2. 注意请求频率限制
3. 在生产环境中使用HTTPS
4. 定期更新API密钥 