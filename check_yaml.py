#!/usr/bin/env python3
"""
YAML 格式检测脚本
检查 manifest.yaml 是否有重复键、格式错误等问题
"""
import yaml
import sys
from pathlib import Path

def check_yaml_format(yaml_file):
    """检查 YAML 文件格式"""
    print(f"🔍 检查 YAML 文件: {yaml_file}")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # 1. 检查文件是否存在
    if not Path(yaml_file).exists():
        print(f"❌ 错误: 文件不存在 - {yaml_file}")
        return False
    
    # 2. 读取并解析 YAML
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            data = yaml.safe_load(content)
        print("✅ YAML 格式正确，没有重复键")
    except yaml.YAMLError as e:
        print(f"❌ YAML 解析错误:")
        print(f"   {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 读取文件错误: {str(e)}")
        return False
    
    # 3. 检查必需字段
    required_fields = ['name', 'version', 'description', 'author', 'entry']
    print("\n📋 检查必需字段:")
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需字段: {field}")
            print(f"   ❌ {field} - 缺失")
        else:
            print(f"   ✅ {field} - {data[field]}")
    
    # 4. 检查版本格式
    print("\n🔢 检查版本号:")
    if 'version' in data:
        version = str(data['version'])
        parts = version.split('.')
        if len(parts) != 3:
            warnings.append(f"版本号格式建议使用 x.y.z 格式，当前: {version}")
            print(f"   ⚠️  版本号格式: {version} (建议使用 x.y.z 格式)")
        else:
            print(f"   ✅ 版本号格式正确: {version}")
    
    # 5. 检查 tool 字段
    print("\n🛠️  检查工具定义:")
    if 'tool' not in data and 'tools' not in data:
        errors.append("缺少 'tool' 或 'tools' 字段")
        print("   ❌ 没有定义任何工具")
    else:
        tools = data.get('tool') or data.get('tools')
        if not isinstance(tools, list):
            errors.append("'tool' 字段必须是列表")
            print("   ❌ 工具定义格式错误（必须是列表）")
        else:
            print(f"   ✅ 定义了 {len(tools)} 个工具:")
            for i, tool in enumerate(tools, 1):
                tool_name = tool.get('name', f'工具{i}')
                if 'name' not in tool:
                    errors.append(f"工具 #{i} 缺少 'name' 字段")
                    print(f"      ❌ #{i}: 缺少名称")
                elif 'parameters' not in tool:
                    errors.append(f"工具 '{tool_name}' 缺少 'parameters' 字段")
                    print(f"      ❌ {tool_name}: 缺少 parameters")
                else:
                    print(f"      ✅ {tool_name}")
    
    # 6. 检查 entry 格式
    print("\n📍 检查入口点:")
    if 'entry' in data:
        entry = data['entry']
        if ':' not in entry:
            warnings.append(f"entry 格式建议为 'module:app'，当前: {entry}")
            print(f"   ⚠️  entry 格式: {entry} (建议格式: module:app)")
        else:
            module, app = entry.split(':', 1)
            print(f"   ✅ 模块: {module}, 应用: {app}")
    
    # 7. 检查描述和标签
    print("\n📝 检查描述和标签:")
    if 'description' in data:
        if isinstance(data['description'], dict):
            if 'en_US' in data['description']:
                print(f"   ✅ description.en_US 已定义")
            else:
                warnings.append("建议添加 description.en_US")
                print(f"   ⚠️  缺少 description.en_US")
        else:
            print(f"   ✅ description 已定义")
    
    if 'tags' in data:
        if isinstance(data['tags'], list):
            print(f"   ✅ tags: {', '.join(data['tags'])}")
        else:
            errors.append("'tags' 必须是列表格式")
            print(f"   ❌ tags 格式错误（必须是列表）")
    
    if 'categories' in data:
        if isinstance(data['categories'], list):
            print(f"   ✅ categories: {', '.join(data['categories'])}")
        else:
            errors.append("'categories' 必须是列表格式")
            print(f"   ❌ categories 格式错误（必须是列表）")
    
    # 8. 检查是否有重复的顶层键（通过原始文本检查）
    print("\n🔍 检查重复键（文本分析）:")
    lines = content.split('\n')
    top_level_keys = {}
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped and not stripped.startswith('#') and ':' in stripped:
            # 检查是否是顶层键（没有缩进或空格开头）
            if line and line[0] not in [' ', '\t', '-']:
                key = stripped.split(':')[0].strip()
                if key in top_level_keys:
                    errors.append(f"第 {i} 行: 键 '{key}' 重复（首次出现在第 {top_level_keys[key]} 行）")
                    print(f"   ❌ 第 {i} 行: '{key}' 重复")
                else:
                    top_level_keys[key] = i
    
    if not errors or len(top_level_keys) == len(set(top_level_keys.keys())):
        print(f"   ✅ 没有发现重复的顶层键")
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 检查结果汇总:")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    
    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    if not errors and not warnings:
        print("\n✅ 所有检查通过！manifest.yaml 格式完全正确！")
        return True
    elif not errors:
        print("\n✅ 没有错误，但有一些警告需要注意")
        return True
    else:
        print(f"\n❌ 检查失败！请修复上述错误后重试")
        return False

if __name__ == '__main__':
    yaml_file = sys.argv[1] if len(sys.argv) > 1 else 'manifest.yaml'
    success = check_yaml_format(yaml_file)
    sys.exit(0 if success else 1)
