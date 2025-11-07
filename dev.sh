#!/bin/bash
# 开发环境启动脚本（支持热重载）

# 加载 .env 文件
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ 已加载 .env 配置"
fi

# 设置默认值
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}
HOST=${HOST:-0.0.0.0}

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Miss Helper Plugin - Development Mode                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "配置信息:"
echo "  - Host: $HOST"
echo "  - Port: $PORT"
echo "  - Log Level: $LOG_LEVEL"
echo "  - CORS: ${CORS_ALLOW_ORIGINS:-*}"
echo "  - Auth Token: $([ -n "$PUBLISH_TOKEN" ] && echo '已设置' || echo '未设置')"
echo ""
echo "开发模式启动中 (支持热重载)..."
echo ""

uvicorn main:app \
    --host "$HOST" \
    --port "$PORT" \
    --log-level "$LOG_LEVEL" \
    --reload
