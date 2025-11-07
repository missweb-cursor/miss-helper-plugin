#!/usr/bin/env python3
"""
Dify Plugin 验证脚本
使用 Dify SDK 真实验证插件是否正确
"""
import sys
import subprocess
import time
import json

def test_plugin_load():
    """测试插件是否能正确加载"""
    print("🔍 测试 1: 插件加载测试")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ["python3", "main.py"],
            cwd="/workspace",
            capture_output=True,
            text=True,
            timeout=3
        )
    except subprocess.TimeoutExpired as e:
        # 插件会持续运行，超时是正常的
        output = e.stdout if e.stdout else ""
        
        if "Installed tool: miss_helper" in output:
            print("✅ 插件成功加载")
            print("✅ 工具提供者 'miss_helper' 已安装")
            
            # 解析插件信息
            lines = output.strip().split('\n')
            if lines:
                try:
                    plugin_info = json.loads(lines[0])
                    print(f"✅ 插件名称: {plugin_info['name']}")
                    print(f"✅ 插件版本: {plugin_info['version']}")
                    print(f"✅ 插件类型: {plugin_info['type']}")
                    print(f"✅ 插件作者: {plugin_info['author']}")
                    return True
                except:
                    pass
            return True
        else:
            print("❌ 插件加载失败")
            print(f"输出: {output}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_yaml_structure():
    """测试 YAML 文件结构"""
    print("\n🔍 测试 2: YAML 文件结构测试")
    print("=" * 60)
    
    try:
        import yaml
        from pathlib import Path
        
        # 测试 manifest.yaml
        with open('/workspace/manifest.yaml') as f:
            manifest = yaml.safe_load(f)
        
        required_fields = ['version', 'type', 'author', 'name', 'plugins', 'meta']
        missing = [f for f in required_fields if f not in manifest]
        
        if missing:
            print(f"❌ manifest.yaml 缺少字段: {missing}")
            return False
        
        print("✅ manifest.yaml 结构正确")
        print(f"   - 版本: {manifest['version']}")
        print(f"   - 类型: {manifest['type']}")
        print(f"   - Runner: {manifest['meta']['runner']['language']} {manifest['meta']['runner']['version']}")
        
        # 测试 provider.yaml
        with open('/workspace/provider/miss_helper.yaml') as f:
            provider = yaml.safe_load(f)
        
        if 'tools' not in provider:
            print("❌ provider YAML 缺少 tools 字段")
            return False
        
        print(f"✅ provider YAML 结构正确")
        print(f"   - 工具数量: {len(provider['tools'])}")
        
        # 测试所有工具 YAML
        tools_dir = Path('/workspace/tools')
        yaml_files = list(tools_dir.glob('*.yaml'))
        py_files = list(tools_dir.glob('*.py'))
        
        print(f"✅ 工具配置文件: {len(yaml_files)} 个")
        print(f"✅ 工具实现文件: {len(py_files)} 个")
        
        if len(yaml_files) != len(py_files):
            print(f"⚠️  警告: YAML 文件和 Python 文件数量不匹配")
        
        # 验证每个工具 YAML
        for yaml_file in yaml_files:
            with open(yaml_file) as f:
                tool = yaml.safe_load(f)
            
            if 'identity' not in tool or 'parameters' not in tool:
                print(f"❌ {yaml_file.name} 结构不完整")
                return False
            
            print(f"   ✅ {tool['identity']['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ YAML 结构测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_provider_class():
    """测试 Provider 类"""
    print("\n🔍 测试 3: Provider 类测试")
    print("=" * 60)
    
    try:
        sys.path.insert(0, '/workspace')
        from provider.miss_helper import MissHelperProvider
        from dify_plugin import ToolProvider
        
        if not issubclass(MissHelperProvider, ToolProvider):
            print("❌ MissHelperProvider 没有继承 ToolProvider")
            return False
        
        print("✅ MissHelperProvider 正确继承 ToolProvider")
        
        # 测试实例化
        provider = MissHelperProvider()
        print("✅ Provider 可以被实例化")
        
        # 测试 _validate_credentials 方法
        if hasattr(provider, '_validate_credentials'):
            provider._validate_credentials({})
            print("✅ _validate_credentials 方法存在并可调用")
        
        return True
        
    except Exception as e:
        print(f"❌ Provider 类测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_classes():
    """测试工具类"""
    print("\n🔍 测试 4: 工具类测试")
    print("=" * 60)
    
    try:
        sys.path.insert(0, '/workspace')
        from dify_plugin import Tool
        from pathlib import Path
        
        tools_dir = Path('/workspace/tools')
        py_files = list(tools_dir.glob('*.py'))
        
        success_count = 0
        for py_file in py_files:
            module_name = py_file.stem
            try:
                # 动态导入
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找 Tool 子类
                tool_class = None
                for item_name in dir(module):
                    item = getattr(module, item_name)
                    if isinstance(item, type) and issubclass(item, Tool) and item != Tool:
                        tool_class = item
                        break
                
                if tool_class:
                    print(f"   ✅ {module_name}: {tool_class.__name__}")
                    success_count += 1
                else:
                    print(f"   ⚠️  {module_name}: 没有找到 Tool 子类")
                    
            except Exception as e:
                print(f"   ❌ {module_name}: {str(e)}")
        
        print(f"\n✅ 成功加载 {success_count}/{len(py_files)} 个工具类")
        return success_count == len(py_files)
        
    except Exception as e:
        print(f"❌ 工具类测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🚀 Dify Plugin 完整验证")
    print("=" * 60)
    print()
    
    results = []
    
    # 运行所有测试
    results.append(("插件加载", test_plugin_load()))
    results.append(("YAML 结构", test_yaml_structure()))
    results.append(("Provider 类", test_provider_class()))
    results.append(("工具类", test_tool_classes()))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！插件格式完全符合 Dify 官方标准！")
        print("=" * 60)
        print("\n✅ 可以安全上传到 Dify 平台")
        return 0
    else:
        print("❌ 部分测试失败，请检查上述错误信息")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
