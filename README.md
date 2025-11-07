# miss_helper_plugin

一个功能丰富的 Dify 插件，提供文本处理、翻译、HTTP 请求等实用工具。

## ✨ 特性

- 🚀 **9个实用工具**: 文本处理、翻译、语言检测、摘要、关键词提取等
- 🔒 **安全**: 支持 Token 认证
- 🌐 **CORS**: 完整的跨域支持
- ⚙️ **灵活配置**: 通过环境变量配置
- 📦 **即插即用**: 符合 Dify 插件标准

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（可选）
cp .env.example .env  # 或直接编辑 .env

# 3. 启动服务
python start.py
# 或开发模式（热重载）
./dev.sh
```

## 📖 详细文档

- [部署指南](DEPLOYMENT.md) - 完整的配置和部署说明
- [标准检查](DIFY_STANDARD_CHECK.md) - Dify 插件标准合规性报告

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

## 🔧 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| PORT | 服务端口 | 8000 |
| LOG_LEVEL | 日志级别 | info |
| PUBLISH_TOKEN | API认证Token | - |
| CORS_ALLOW_ORIGINS | CORS来源 | * |

详见 [DEPLOYMENT.md](DEPLOYMENT.md)

## 📡 API 示例

```bash
# 健康检查
curl http://localhost:8000/health

# 调用工具
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool": "echo_text", "parameters": {"text": "Hello"}}'
```

## 📄 许可

MIT License

## 👤 作者

missweb-cursor
