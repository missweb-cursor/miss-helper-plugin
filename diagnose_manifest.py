#!/usr/bin/env python3
"""
manifest.yaml 诊断工具
帮助找出YAML文件的具体问题
"""
import sys
import yaml

def diagnose_manifest(file_path):
    print("=" * 70)
    print(f"  诊断文件: {file_path}")
    print("=" * 70)
    
    # 1. 读取文件
    print("\n[1] 读取文件...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"  ✓ 文件读取成功 ({len(content)} 字节)")
    except Exception as e:
        print(f"  ✗ 文件读取失败: {e}")
        return False
    
    # 2. 检查文件编码
    print("\n[2] 检查编码...")
    try:
        content.encode('utf-8')
        print("  ✓ UTF-8 编码正常")
    except Exception as e:
        print(f"  ✗ 编码问题: {e}")
        return False
    
    # 3. 解析YAML
    print("\n[3] 解析 YAML...")
    try:
        manifest = yaml.safe_load(content)
        print("  ✓ YAML 解析成功")
    except yaml.YAMLError as e:
        print(f"  ✗ YAML 语法错误:")
        print(f"     {e}")
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            print(f"     位置: 行{mark.line + 1}, 列{mark.column + 1}")
            # 显示错误行
            lines = content.split('\n')
            if mark.line < len(lines):
                print(f"     内容: {lines[mark.line]}")
                print(f"           {' ' * mark.column}^")
        return False
    
    # 4. 检查必需字段
    print("\n[4] 检查必需字段...")
    
    # 检测是哪种格式
    if 'plugins' in manifest:
        print("  检测到新格式 (带 plugins 字段)")
        required_fields = {
            'version': '版本',
            'type': '类型',
            'name': '名称',
            'label': '标签',
            'description': '描述',
            'plugins': '插件定义'
        }
    else:
        print("  检测到旧格式")
        required_fields = {
            'name': '名称',
            'version': '版本',
            'description': '描述',
            'labels': '标签',
            'author': '作者',
            'entry': '入口点',
            'tool': '工具列表'
        }
    
    missing = []
    for field, desc in required_fields.items():
        if field in manifest:
            value = manifest[field]
            if isinstance(value, (dict, list)):
                print(f"  ✓ {desc} ({field}): {type(value).__name__}")
            else:
                print(f"  ✓ {desc} ({field}): {value}")
        else:
            print(f"  ✗ 缺少 {desc} ({field})")
            missing.append(field)
    
    if missing:
        print(f"\n  ⚠ 缺少 {len(missing)} 个必需字段")
        return False
    
    # 5. 检查工具定义
    print("\n[5] 检查工具定义...")
    if 'plugins' in manifest:
        tools = manifest.get('plugins', {}).get('tools', [])
    else:
        tools = manifest.get('tool', [])
    
    if not tools:
        print("  ✗ 没有定义任何工具")
        return False
    
    print(f"  ✓ 定义了 {len(tools)} 个工具")
    
    # 检查每个工具
    all_valid = True
    for i, tool in enumerate(tools, 1):
        tool_name = tool.get('name', f'工具{i}')
        print(f"\n  工具 {i}: {tool_name}")
        
        # 检查必需字段
        tool_required = ['name', 'label', 'description', 'parameters']
        tool_missing = [f for f in tool_required if f not in tool]
        
        if tool_missing:
            print(f"    ✗ 缺少字段: {', '.join(tool_missing)}")
            all_valid = False
        else:
            print(f"    ✓ 必需字段完整")
        
        # 检查 label 和 description 是否有 en_US
        if 'label' in tool:
            if isinstance(tool['label'], dict):
                if 'en_US' not in tool['label']:
                    print(f"    ⚠ label 缺少 en_US")
                    all_valid = False
            elif not isinstance(tool['label'], str):
                print(f"    ⚠ label 格式错误")
                all_valid = False
        
        if 'description' in tool:
            if isinstance(tool['description'], dict):
                if 'en_US' not in tool['description']:
                    print(f"    ⚠ description 缺少 en_US")
                    all_valid = False
        
        # 检查 parameters
        if 'parameters' in tool:
            params = tool['parameters']
            if isinstance(params, dict):
                # 旧格式
                if 'type' not in params:
                    print(f"    ⚠ parameters 缺少 type")
                    all_valid = False
                if 'properties' not in params:
                    print(f"    ⚠ parameters 缺少 properties")
                    all_valid = False
            elif isinstance(params, list):
                # 新格式
                print(f"    ✓ parameters 包含 {len(params)} 个参数")
            else:
                print(f"    ✗ parameters 格式错误")
                all_valid = False
    
    # 6. 总结
    print("\n" + "=" * 70)
    if all_valid:
        print("  ✅ 所有检查通过！manifest.yaml 格式正确")
        return True
    else:
        print("  ⚠️  发现一些问题，但可能不影响使用")
        return True

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'manifest.yaml'
    
    success = diagnose_manifest(file_path)
    
    print("\n" + "=" * 70)
    print("  提示:")
    print("=" * 70)
    print("  - 如果YAML语法错误，请检查缩进和特殊字符")
    print("  - Dify支持两种manifest格式:")
    print("    1. 旧格式: 使用 'tool' 字段")
    print("    2. 新格式: 使用 'plugins.tools' 字段")
    print("  - 当前目录有两个版本:")
    print("    manifest.yaml  - 旧格式（当前）")
    print("    _manifest.yaml - 新格式（备用）")
    print("\n  如果旧格式有问题，可以尝试:")
    print("    mv manifest.yaml manifest.yaml.bak")
    print("    mv _manifest.yaml manifest.yaml")
    
    sys.exit(0 if success else 1)
