#!/usr/bin/env python3
"""
流式聊天服务示例
演示如何使用阿里云百炼API进行流式对话
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.stream_chat_service import StreamChatService


async def main():
    """主函数"""
    print("=== 阿里云百炼流式聊天服务示例 ===")
    
    try:
        # 初始化流式聊天服务
        chat_service = StreamChatService()
        print(f"✅ 聊天服务初始化成功")
        print(f"📝 使用模型: {chat_service.model}")
        print()
        
        # 测试消息
        test_messages = [
            "北京今天天气怎么样？"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"🤖 测试 {i}: {message}")
            print("📤 发送消息...")
            print("📥 接收回复:")
            
            # 流式接收回复
            async for chunk in chat_service.stream_chat(message):
                if chunk["type"] == "stream_start":
                    print("🚀 开始流式传输...")
                elif chunk["type"] == "stream_chunk":
                    print(chunk["chunk"], end="", flush=True)
                elif chunk["type"] == "stream_end":
                    print("\n✅ 流式传输完成")
                elif chunk["type"] == "error":
                    print(f"\n❌ 错误: {chunk['error']}")
            
            print("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        print("\n💡 请确保已正确配置阿里云百炼API密钥:")
        print("   在.env文件中设置DASHSCOPE_API_KEY")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main()) 