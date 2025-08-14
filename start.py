"""
Geo-Agent 启动脚本
支持选择AI模型和配置检查
"""
import os
import sys
from dotenv import load_dotenv

def check_config():
    """检查配置"""
    print("🔍 检查配置...")
    
    # 加载环境变量
    load_dotenv()
    
    ai_provider = os.getenv("AI_PROVIDER", "qwen").lower()
    print(f"AI提供商: {ai_provider}")
    
    if ai_provider == "qwen":
        qwen_key = os.getenv("QWEN_API_KEY")
        if not qwen_key:
            print("❌ QWEN_API_KEY 未配置")
            print("请在 .env 文件中设置:")
            print("AI_PROVIDER=qwen")
            print("QWEN_API_KEY=your_qwen_api_key_here")
            return False
        print("✅ Qwen-Flash 配置正确")
        
    elif ai_provider == "openai":
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("❌ OPENAI_API_KEY 未配置")
            print("请在 .env 文件中设置:")
            print("AI_PROVIDER=openai")
            print("OPENAI_API_KEY=your_openai_api_key_here")
            return False
        print("✅ OpenAI 配置正确")
        
    else:
        print(f"❌ 不支持的AI提供商: {ai_provider}")
        print("支持的提供商: openai, qwen")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 Geo-Agent 启动脚本")
    print("=" * 40)
    
    # 检查配置
    if not check_config():
        print("\n❌ 配置检查失败，请修复后重试")
        sys.exit(1)
    
    print("\n✅ 配置检查通过！")
    
    print("\n🧪 运行测试...")
        
    # 运行Qwen测试
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_qwen.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Qwen-Flash 测试通过")
        else:
            print("❌ Qwen-Flash 测试失败")
            print(result.stderr)
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")


    print("\n🚀 启动服务...")
    try:
        import subprocess
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {str(e)}")


if __name__ == "__main__":
    main() 