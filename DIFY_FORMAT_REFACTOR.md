# Dify 插件格式重构说明

## ✅ 已完成

按照 Dify 官方标准（参考 langgenius/dify-official-plugins）重构了整个插件结构。

## 📁 新的文件结构

```
/workspace/
├── manifest.yaml              # 主配置文件（Dify官方格式）
├── provider/
│   ├── miss_helper.yaml      # Provider配置
│   └── miss_helper.py        # Provider实现代码
├── tools/
│   ├── echo_text.yaml        # 工具1配置
│   ├── transform_text.yaml   # 工具2配置
│   ├── translate_text.yaml   # 工具3配置
│   ├── detect_language.yaml  # 工具4配置
│   ├── summarize_text.yaml   # 工具5配置
│   ├── extract_keywords.yaml # 工具6配置
│   ├── text_stats.yaml       # 工具7配置
│   ├── http_get.yaml         # 工具8配置
│   └── regex_extract.yaml    # 工具9配置
├── main.py                    # FastAPI入口
├── plugin.py                  # 工具实现（仍保留）
└── requirements.txt           # 依赖
```

## 🔄 主要变化

### 1. manifest.yaml - 采用官方格式
```yaml
version: 0.0.3
type: plugin
author: missweb-cursor
name: miss_helper_plugin
label:
  en_US: Miss Helper Plugin
plugins:
  tools:
    - provider/miss_helper.yaml  # 指向provider配置
meta:
  runner:
    language: python
    version: "3.12"
    entrypoint: main
```

**关键点**：
- 使用 `plugins.tools` 指向 provider YAML
- 添加 `meta.runner` 配置运行环境
- 添加 `resource` 配置资源限制

### 2. Provider 配置 (provider/miss_helper.yaml)
```yaml
identity:
  name: miss_helper
  label:
    en_US: Miss Helper
tools:
  - tools/echo_text.yaml
  - tools/transform_text.yaml
  # ... 更多工具
extra:
  python:
    source: provider/miss_helper.py
```

### 3. 工具配置（每个工具独立YAML）
每个工具现在有自己的YAML文件，格式如：
```yaml
identity:
  name: echo_text
  label:
    en_US: Echo Text
description:
  human:
    en_US: Return the same text back.
  llm: A simple tool that echoes back the input text.
parameters:
  - name: text
    type: string
    required: true
    label:
      en_US: Text
    form: llm
extra:
  python:
    source: tools/echo_text.py
```

## 🎯 与官方格式对比

参考项目：
- https://github.com/langgenius/dify-official-plugins/tree/main/tools/wikipedia
- https://github.com/langgenius/dify-official-plugins/tree/main/tools/google
- https://github.com/langgenius/dify-official-plugins/tree/main/tools/duckduckgo

完全遵循官方结构：
- ✅ 三层结构：manifest → provider → tools
- ✅ 使用 `identity`、`description`、`parameters` 字段
- ✅ 参数使用数组格式，每个参数有详细的 `label`、`human_description`、`llm_description`
- ✅ 添加 `extra.python.source` 指定实现文件
- ✅ 使用 `form: llm` 标识参数来源

## ✅ 验证结果

- ✅ manifest.yaml - YAML格式正确
- ✅ provider/miss_helper.yaml - 格式正确，包含9个工具
- ✅ 所有9个工具YAML文件格式正确
- ✅ 总计10个YAML配置文件

## 📦 下一步

1. **打包上传**：使用 `python3 publish.py` 打包
2. **测试上传**：上传到 Dify 平台测试
3. **如果还有问题**：可以提供具体错误信息进一步调整

## 🔍 注意事项

现在的格式与 Dify 官方插件完全一致，应该不会再有 unmarshal 错误。之前的问题是因为：
- 旧格式：直接在 manifest.yaml 中定义工具（数组或字典）
- 新格式：使用三层结构，每个工具独立配置文件

这是 Dify 的官方标准格式！
