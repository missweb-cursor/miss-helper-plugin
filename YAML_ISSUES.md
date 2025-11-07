# manifest.yaml 问题排查指南

## 📋 当前状态

我已经创建了**两个版本**的manifest.yaml：

1. **manifest.yaml** (当前使用) - 旧格式
   - 使用 `tool` 字段定义工具
   - JSON Schema格式的参数定义
   - 适用于大多数Dify版本

2. **_manifest.yaml** (备用) - 新格式  
   - 使用 `plugins.tools` 字段
   - 更详细的参数定义(包含label、human_description等)
   - 添加了中文(zh_Hans)支持
   - 适用于新版Dify

**两个版本的YAML语法都是正确的！** ✅

## 🔍 请告诉我具体错误

为了帮你解决问题，我需要知道：

### 1. 具体的错误信息是什么？

请复制完整的错误信息，例如：
- "YAML parsing error..."
- "Invalid manifest format..."
- "Missing field..."
- 或Dify界面显示的任何错误

### 2. 在哪个步骤出错？

- [ ] 上传/导入manifest.yaml时
- [ ] 保存插件配置时
- [ ] 启动插件时
- [ ] 调用工具时
- [ ] 其他（请说明）

### 3. Dify版本是什么？

不同版本的Dify可能支持不同的manifest格式。

## 🔧 快速切换格式

如果当前格式有问题，可以尝试另一个格式：

```bash
# 备份当前版本
cp manifest.yaml manifest.yaml.old

# 使用新格式
cp _manifest.yaml manifest.yaml

# 如果需要还原
# cp manifest.yaml.old manifest.yaml
```

## 🧪 测试工具

我创建了诊断工具，运行它查看详细信息：

```bash
python3 diagnose_manifest.py manifest.yaml
python3 diagnose_manifest.py _manifest.yaml
```

## 📝 手动检查清单

如果你看到具体错误，检查以下项目：

### YAML语法错误
- [ ] 缩进是否使用空格（不是Tab）
- [ ] 引号是否配对
- [ ] 列表项是否正确使用 `-`
- [ ] 特殊字符是否正确转义

### 字段缺失
- [ ] name - 插件名称
- [ ] version - 版本号
- [ ] description - 描述（必须有en_US）
- [ ] labels 或 label - 标签
- [ ] author - 作者
- [ ] entry - 入口点（main:app）

### 工具定义
- [ ] 每个工具有name
- [ ] 每个工具有label（包含en_US）
- [ ] 每个工具有description（包含en_US）
- [ ] 每个工具有parameters

## 💡 常见问题修复

### 问题1: "labels字段缺失"
```yaml
# 错误
label:
  en_US: "Plugin Name"

# 正确（旧格式）
labels:
  en_US: "Plugin Name"
```

### 问题2: "tool字段格式错误"
```yaml
# 错误
tool: echo_text

# 正确
tool:
  - name: echo_text
    label: ...
```

### 问题3: "parameters格式错误"
旧格式使用JSON Schema：
```yaml
parameters:
  type: object
  properties:
    text:
      type: string
```

新格式使用数组：
```yaml
parameters:
  - name: text
    type: string
    required: true
```

## 🆘 下一步

请告诉我：
1. **具体的错误信息**（完整复制）
2. **出错的位置**（上传？启动？调用？）
3. **Dify版本**（如果知道）

然后我可以精确地修复问题！

---

**当前两个manifest文件都通过了语法检查**，所以问题可能是：
- Dify版本兼容性
- 网络/连接问题
- 其他配置问题

不是YAML本身的语法问题。
