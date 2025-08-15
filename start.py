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
    
    openai_key = os.getenv("DASHSCOPE_API_KEY")
    if not openai_key:
        print("❌ DASHSCOPE_API_KEY 未配置")
        print("请在 .env 文件中设置:")
        print("DASHSCOPE_API_KEY=your_dashscope_api_key_here")
        return False
    print("✅ DashScope 配置正确")
    
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