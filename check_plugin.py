#!/usr/bin/env python3
"""
插件完整性检测脚本
检查整个插件是否符合 Dify 插件规范
"""
import sys
import yaml
import importlib.util
from pathlib import Path

def check_plugin_structure():
    """检查插件结构完整性"""
    print("🔍 Dify 插件完整性检查")
    print("=" * 60)
    
    errors = []
    warnings = []
    success_count = 0
    
    # 1. 检查必需文件
    print("\n📁 检查必需文件:")
    required_files = {
        'manifest.yaml': '插件配置文件',
        'main.py': '主入口文件',
        'requirements.txt': '依赖文件'
    }
    
    for filename, description in required_files.items():
        if Path(filename).exists():
            print(f"   ✅ {filename} - {description}")
            success_count += 1
        else:
            errors.append(f"缺少必需文件: {filename} ({description})")
            print(f"   ❌ {filename} - 缺失")
    
    # 2. 检查可选文件
    print("\n📄 检查可选文件:")
    optional_files = {
        'README.md': '说明文档',
        'icon.png': '插件图标',
        'plugin.py': '插件实现文件'
    }
    
    for filename, description in optional_files.items():
        if Path(filename).exists():
            print(f"   ✅ {filename} - {description}")
        else:
            print(f"   ⚠️  {filename} - 未找到 ({description})")
    
    # 3. 解析并验证 manifest.yaml
    print("\n📋 检查 manifest.yaml 内容:")
    manifest_data = None
    try:
        with open('manifest.yaml', 'r', encoding='utf-8') as f:
            manifest_data = yaml.safe_load(f)
        print("   ✅ YAML 格式正确")
        
        # 检查入口点
        if 'entry' in manifest_data:
            entry = manifest_data['entry']
            print(f"   ✅ 入口点: {entry}")
            
            # 验证入口点格式
            if ':' in entry:
                module_name, app_name = entry.split(':', 1)
                
                # 检查模块文件是否存在
                module_file = f"{module_name}.py"
                if Path(module_file).exists():
                    print(f"      ✅ 模块文件存在: {module_file}")
                else:
                    errors.append(f"入口模块文件不存在: {module_file}")
                    print(f"      ❌ 模块文件不存在: {module_file}")
            else:
                warnings.append(f"入口点格式可能不正确: {entry}")
                print(f"      ⚠️  入口点格式: {entry}")
        
        # 检查工具数量（支持列表和字典格式）
        tools = manifest_data.get('tool') or manifest_data.get('tools')
        if tools:
            tool_count = len(tools) if isinstance(tools, (list, dict)) else 0
            if tool_count > 0:
                print(f"   ✅ 定义了 {tool_count} 个工具")
            else:
                warnings.append("没有定义任何工具")
                print(f"   ⚠️  没有定义工具")
        else:
            warnings.append("没有定义任何工具")
            print(f"   ⚠️  没有定义工具")
            
    except FileNotFoundError:
        errors.append("找不到 manifest.yaml 文件")
        print("   ❌ 文件不存在")
    except yaml.YAMLError as e:
        errors.append(f"YAML 格式错误: {str(e)}")
        print(f"   ❌ YAML 格式错误")
    except Exception as e:
        errors.append(f"读取 manifest.yaml 失败: {str(e)}")
        print(f"   ❌ 读取失败: {str(e)}")
    
    # 4. 检查 main.py 语法
    print("\n🐍 检查 Python 文件语法:")
    python_files = ['main.py', 'plugin.py']
    for py_file in python_files:
        if Path(py_file).exists():
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, py_file, 'exec')
                print(f"   ✅ {py_file} - 语法正确")
            except SyntaxError as e:
                errors.append(f"{py_file} 语法错误: {e.msg} (第 {e.lineno} 行)")
                print(f"   ❌ {py_file} - 语法错误: {e.msg} (第 {e.lineno} 行)")
            except Exception as e:
                warnings.append(f"{py_file} 检查失败: {str(e)}")
                print(f"   ⚠️  {py_file} - 检查失败: {str(e)}")
    
    # 5. 检查 requirements.txt
    print("\n📦 检查依赖文件:")
    if Path('requirements.txt').exists():
        try:
            with open('requirements.txt', 'r', encoding='utf-8') as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if deps:
                print(f"   ✅ 定义了 {len(deps)} 个依赖:")
                for dep in deps[:5]:  # 只显示前5个
                    print(f"      - {dep}")
                if len(deps) > 5:
                    print(f"      ... 还有 {len(deps) - 5} 个")
            else:
                warnings.append("requirements.txt 为空")
                print(f"   ⚠️  文件为空")
        except Exception as e:
            warnings.append(f"读取 requirements.txt 失败: {str(e)}")
            print(f"   ⚠️  读取失败: {str(e)}")
    
    # 6. 检查工具函数实现
    if manifest_data and Path('main.py').exists():
        print("\n🛠️  检查工具函数实现:")
        try:
            # 尝试导入模块
            spec = importlib.util.spec_from_file_location("main", "main.py")
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 检查是否有 app 对象
                if hasattr(module, 'app'):
                    print("   ✅ 找到 app 对象")
                    app = module.app
                    
                    # 检查每个工具是否有对应的函数
                    tools = manifest_data.get('tool') or manifest_data.get('tools')
                    if isinstance(tools, list):
                        # 旧格式：列表
                        tool_names = [tool.get('name') for tool in tools if tool.get('name')]
                    elif isinstance(tools, dict):
                        # 新格式：字典（工具名作为 key）
                        tool_names = list(tools.keys())
                    else:
                        tool_names = []
                    
                    for tool_name in tool_names:
                        # 检查是否有对应的处理函数
                        if hasattr(app, tool_name) or tool_name in dir(module):
                            print(f"      ✅ 工具 '{tool_name}' 已实现")
                        else:
                            warnings.append(f"工具 '{tool_name}' 可能未实现")
                            print(f"      ⚠️  工具 '{tool_name}' 未找到实现")
                else:
                    warnings.append("main.py 中未找到 'app' 对象")
                    print("   ⚠️  未找到 'app' 对象")
        except Exception as e:
            warnings.append(f"无法加载 main.py: {str(e)}")
            print(f"   ⚠️  无法加载模块: {str(e)}")
    
    # 7. 检查文件大小
    print("\n📊 检查文件大小:")
    total_size = 0
    for file_path in Path('.').glob('**/*'):
        if file_path.is_file() and not str(file_path).startswith('.'):
            size = file_path.stat().st_size
            total_size += size
            if size > 1024 * 1024:  # 大于 1MB
                warnings.append(f"文件较大: {file_path} ({size / 1024 / 1024:.2f} MB)")
                print(f"   ⚠️  {file_path}: {size / 1024 / 1024:.2f} MB")
    
    print(f"   ℹ️  总大小: {total_size / 1024:.2f} KB")
    if total_size > 10 * 1024 * 1024:  # 大于 10MB
        warnings.append(f"插件总大小较大: {total_size / 1024 / 1024:.2f} MB")
    
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
        print("\n✅✅✅ 所有检查通过！插件结构完整，可以上传！")
        return True
    elif not errors:
        print("\n✅ 没有严重错误，插件应该可以正常上传")
        print("   建议修复上述警告以获得更好的用户体验")
        return True
    else:
        print(f"\n❌ 检查失败！请修复上述 {len(errors)} 个错误后重试")
        return False

if __name__ == '__main__':
    success = check_plugin_structure()
    sys.exit(0 if success else 1)
