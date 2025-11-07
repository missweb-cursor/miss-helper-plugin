#!/bin/bash
# Dify 插件快速测试脚本

set -e

echo "=========================================="
echo "  Dify 插件快速测试"
echo "=========================================="

# 检查依赖
echo ""
echo "[1] 检查 Python 环境"
python3 --version || { echo "错误: Python3 未安装"; exit 1; }

echo ""
echo "[2] 检查文件"
for file in manifest.yaml main.py plugin.py requirements.txt; do
    if [ -f "$file" ]; then
        echo "  ✓ $file 存在"
    else
        echo "  ✗ $file 不存在"
        exit 1
    fi
done

echo ""
echo "[3] 检查 Python 语法"
python3 -m py_compile main.py || { echo "  ✗ main.py 语法错误"; exit 1; }
python3 -m py_compile plugin.py || { echo "  ✗ plugin.py 语法错误"; exit 1; }
echo "  ✓ Python 语法正确"

echo ""
echo "[4] 检查 manifest.yaml"
python3 << 'PYEOF'
import yaml
try:
    with open('manifest.yaml', 'r') as f:
        manifest = yaml.safe_load(f)
    
    required = ['name', 'version', 'description', 'labels', 'author', 'entry', 'tool']
    missing = [f for f in required if f not in manifest]
    
    if missing:
        print(f"  ✗ 缺少字段: {', '.join(missing)}")
        exit(1)
    
    print(f"  ✓ manifest.yaml 正确 ({len(manifest['tool'])} 个工具)")
except Exception as e:
    print(f"  ✗ manifest.yaml 错误: {e}")
    exit(1)
PYEOF

echo ""
echo "[5] 检查依赖安装"
echo "  提示: 如果未安装依赖，运行: pip install -r requirements.txt"
echo ""
echo "=========================================="
echo "  ✅ 所有检查通过！"
echo "=========================================="
echo ""
echo "启动插件:"
echo "  python start.py"
echo ""
echo "或开发模式:"
echo "  ./dev.sh"
echo ""
echo "测试命令:"
echo "  curl http://localhost:8000/health"
echo "  curl -X POST http://localhost:8000/invoke \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"tool\":\"echo_text\",\"parameters\":{\"text\":\"Hello\"}}'"
echo ""
