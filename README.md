# Route B — All-in-One Managed Hosting Plugin (miss_砖哥助手)

零改动可运行：
- 默认端口 8000，CORS 全开
- 不强制鉴权（未设置 PUBLISH_TOKEN 时）
- 翻译默认使用公共 LibreTranslate API：`https://libretranslate.de/translate`

## 运行
```bash
pip install -r requirements.txt
python main.py
# 健康检查: http://127.0.0.1:8000/health
```

## Dify API 扩展配置
- Endpoint: `https://你的域名/invoke`
- （可选）Header: `X-Plugin-Token: <如果你设置了 PUBLISH_TOKEN>`
- 工具名与参数见 `manifest.json` 或 GET `/tools`

## 示例调用
```bash
# echo
curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json"   -d '{"tool":"echo_text","parameters":{"text":"hello"}}'

# translate（默认公共 API）
curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json"   -d '{"tool":"translate_text","parameters":{"text":"你好世界","target_lang":"en"}}'

# detect language
curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json"   -d '{"tool":"detect_language","parameters":{"text":"Bonjour le monde"}}'

# summarize
curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json"   -d '{"tool":"summarize_text","parameters":{"text":"段落一。段落二。段落三。段落四。","sentences":2}}'
```
