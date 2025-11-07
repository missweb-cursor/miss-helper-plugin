# Dify 插件开发与部署指南

## 📋 环境配置

### 1. 创建 .env 文件

项目已包含 `.env` 文件，配置如下：

```bash
# Dify 远程调试配置
INSTALL_METHOD=remote
REMOTE_INSTALL_URL=debug.dify.ai:5003
REMOTE_INSTALL_KEY=77d897e5-3df3-4f2c-aa38-25e779192ce8

# 服务器配置
PORT=8000              # 服务端口
LOG_LEVEL=info         # 日志级别: debug, info, warning, error
PUBLISH_TOKEN=change_me_in_debug  # API鉴权Token

# 翻译服务配置（可选）
TRANSLATE_API_URL=     # LibreTranslate API 地址
TRANSLATE_API_KEY=     # API密钥

# CORS 跨域配置
CORS_ALLOW_ORIGINS=*   # 允许的来源，* 表示全部
```

## 🚀 快速开始

### 方式 1: 使用 Python 启动脚本（推荐）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python start.py
```

### 方式 2: 使用开发脚本（支持热重载）

```bash
# 开发模式 - 代码修改后自动重启
./dev.sh
```

### 方式 3: 直接使用 uvicorn

```bash
# 手动指定参数
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info

# 开发模式（热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `PORT` | 服务端口 | 8000 | 否 |
| `HOST` | 监听地址 | 0.0.0.0 | 否 |
| `LOG_LEVEL` | 日志级别 | info | 否 |
| `PUBLISH_TOKEN` | API鉴权Token | - | 否 |
| `CORS_ALLOW_ORIGINS` | CORS来源 | * | 否 |
| `TRANSLATE_API_URL` | 翻译API地址 | - | 否 |
| `TRANSLATE_API_KEY` | 翻译API密钥 | - | 否 |

## 📡 API 端点

### 1. 健康检查
```bash
GET /health
```

### 2. 工具列表
```bash
GET /tools
```

### 3. 调用工具
```bash
POST /invoke
Content-Type: application/json
X-Plugin-Token: <your-token>  # 如果设置了 PUBLISH_TOKEN

{
  "tool": "echo_text",
  "parameters": {
    "text": "Hello World"
  }
}
```

## 🧪 测试插件

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 测试 echo_text 工具
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool": "echo_text", "parameters": {"text": "Hello"}}'

# 3. 带认证的请求
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -H "X-Plugin-Token: change_me_in_debug" \
  -d '{"tool": "transform_text", "parameters": {"text": "hello", "mode": "upper"}}'
```

## 🛠️ 工具列表

1. **echo_text** - 回显文本
2. **transform_text** - 文本转换（大写/小写/反转）
3. **translate_text** - 文本翻译
4. **detect_language** - 语言检测
5. **summarize_text** - 文本摘要
6. **extract_keywords** - 关键词提取
7. **text_stats** - 文本统计
8. **http_get** - HTTP GET 请求
9. **regex_extract** - 正则表达式提取

## 🐛 调试模式

在 Dify 中配置远程调试：

1. 在 Dify 中添加插件
2. 选择"远程安装"模式
3. 填入配置：
   - URL: `debug.dify.ai:5003`
   - Key: `77d897e5-3df3-4f2c-aa38-25e779192ce8`
4. 本地启动插件服务
5. 在 Dify 中测试工具

## 📦 生产部署

### Docker 部署（推荐）

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "start.py"]
```

```bash
# 构建镜像
docker build -t miss-helper-plugin .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -e PUBLISH_TOKEN=your-secret-token \
  -e CORS_ALLOW_ORIGINS=https://your-dify.com \
  --name miss-helper \
  miss-helper-plugin
```

### 直接部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
export PORT=8000
export PUBLISH_TOKEN=your-secret-token
export CORS_ALLOW_ORIGINS=https://your-dify.com

# 3. 启动服务
python start.py
```

## 🔒 安全建议

1. **生产环境必须设置 PUBLISH_TOKEN**
2. **限制 CORS_ALLOW_ORIGINS 到特定域名**
3. **使用 HTTPS**
4. **定期更新依赖包**

## 📝 开发注意事项

- 所有工具函数必须返回 `{"text": "结果"}` 格式
- manifest.yaml 中的工具定义必须与代码一致
- 支持的日志级别: debug, info, warning, error, critical

## ❓ 常见问题

**Q: 如何更改端口？**
A: 在 .env 文件中修改 `PORT=8000` 或启动时设置环境变量

**Q: 如何关闭认证？**
A: 不设置 `PUBLISH_TOKEN` 或设置为空

**Q: CORS 错误怎么办？**
A: 检查 `CORS_ALLOW_ORIGINS` 设置，确保包含 Dify 的域名
