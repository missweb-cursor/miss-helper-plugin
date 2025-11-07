#!/usr/bin/env python3
"""
启动脚本 - 支持从环境变量读取配置
用法: python start.py
"""
import os
import sys

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ 已加载 .env 配置文件")
except ImportError:
    print("⚠ python-dotenv 未安装，使用系统环境变量")
except Exception as e:
    print(f"⚠ 加载 .env 失败: {e}")

import uvicorn

# 从环境变量读取配置
PORT = int(os.getenv("PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").lower()
HOST = os.getenv("HOST", "0.0.0.0")

# 验证日志级别
valid_log_levels = ["critical", "error", "warning", "info", "debug", "trace"]
if LOG_LEVEL not in valid_log_levels:
    print(f"警告: 无效的日志级别 '{LOG_LEVEL}'，使用默认值 'info'")
    LOG_LEVEL = "info"

print(f"""
╔════════════════════════════════════════════════════════════╗
║          Miss Helper Plugin Starting...                   ║
╚════════════════════════════════════════════════════════════╝

配置信息:
  - Host: {HOST}
  - Port: {PORT}
  - Log Level: {LOG_LEVEL}
  - CORS: {os.getenv('CORS_ALLOW_ORIGINS', '*')}
  - Auth Token: {'已设置' if os.getenv('PUBLISH_TOKEN') else '未设置'}

启动中...
""")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        log_level=LOG_LEVEL,
        reload=False  # 生产环境建议关闭热重载
    )
