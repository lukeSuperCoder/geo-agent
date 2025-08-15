#!/usr/bin/env python3
"""
API流式测试 - 意图解析
"""
import asyncio
import aiohttp
import json


async def test_api_stream(message=None):
    """测试API流式效果"""
    print("🧪 API意图解析测试")
    print("=" * 40)
    
    # 如果没有提供消息，则手动输入
    if message is None:
        message = input("请输入您想说的话: ").strip()
        if not message:
            print("❌ 消息不能为空")
            return
    
    url = "http://localhost:8000/api/chat/stream"
    data = {
        "message": message,
        "session_id": "api_test"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                print(f"📡 状态: {response.status}")
                
                if response.status == 200:
                    print("📥 接收流式数据:")
                    print("-" * 30)
                    
                    count = 0
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str.strip():
                                try:
                                    parsed = json.loads(data_str)
                                    count += 1
                                    
                                    if parsed["type"] == "stream_start":
                                        print(f"[{count:2d}] 🚀 开始意图解析")
                                    elif parsed["type"] == "intent_parsed":
                                        intent = parsed["intent"]
                                        print(f"[{count:2d}] 🎯 意图解析完成:")
                                        print(f"    意图类型: {intent['intent']}")
                                        print(f"    置信度: {intent['confidence']}")
                                        print(f"    参数: {intent['parameters']}")
                                        
                                        # 根据意图类型给出建议
                                        if intent['intent'] == 'weather_query':
                                            print("💡 建议: 调用天气插件获取实时天气数据")
                                        elif intent['intent'] == 'poi_search':
                                            print("💡 建议: 调用POI搜索插件获取兴趣点信息")
                                        elif intent['intent'] == 'route_planning':
                                            print("💡 建议: 调用路径规划插件计算路线")
                                        elif intent['intent'] == 'map_fly_to':
                                            print("💡 建议: 执行地图飞行操作")
                                        elif intent['intent'] == 'location_search':
                                            print("💡 建议: 执行地点搜索")
                                        elif intent['intent'] == 'unknown':
                                            print("💡 建议: 返回通用回复或询问用户具体需求")
                                            
                                    elif parsed["type"] == "stream_end":
                                        print(f"[{count:2d}] ✅ 解析完成")
                                        break
                                    elif parsed["type"] == "error":
                                        print(f"[{count:2d}] ❌ 错误: {parsed['error']}")
                                        break
                                        
                                except json.JSONDecodeError:
                                    print(f"[{count:2d}] ❌ JSON错误")
                else:
                    print(f"❌ 失败: {response.status}")
                    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("=" * 40)


async def interactive_chat():
    """交互式意图解析模式"""
    print("💬 交互式意图解析模式")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 40)
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n💭 您: ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("👋 再见!")
                break
            
            if not user_input:
                print("❌ 消息不能为空，请重新输入")
                continue
            
            # 发送消息并获取响应
            await test_api_stream(user_input)
            
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")


if __name__ == "__main__":
    import sys
    
    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 如果有参数，使用第一个参数作为消息
        message = " ".join(sys.argv[1:])
        asyncio.run(test_api_stream(message))
    else:
        # 否则进入交互模式
        asyncio.run(interactive_chat()) 