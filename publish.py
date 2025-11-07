#!/usr/bin/env python3
"""
自动检测、修复和发布插件
一键完成所有流程
"""
import os
import sys
import yaml
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime

class PluginPublisher:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.workspace = Path('/workspace')
        
    def print_header(self, title):
        """打印标题"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)
    
    def step(self, msg):
        """打印步骤"""
        print(f"\n🔹 {msg}")
    
    def success(self, msg):
        """打印成功信息"""
        print(f"   ✅ {msg}")
    
    def error(self, msg):
        """打印错误信息"""
        print(f"   ❌ {msg}")
        self.errors.append(msg)
    
    def warning(self, msg):
        """打印警告信息"""
        print(f"   ⚠️  {msg}")
        self.warnings.append(msg)
    
    def info(self, msg):
        """打印信息"""
        print(f"   ℹ️  {msg}")
    
    def check_yaml(self):
        """检查 YAML 文件"""
        self.step("检查 manifest.yaml")
        
        yaml_file = self.workspace / 'manifest.yaml'
        if not yaml_file.exists():
            self.error("manifest.yaml 文件不存在")
            return False
        
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                data = yaml.safe_load(content)
            
            # 检查必需字段
            required = ['name', 'version', 'description', 'author', 'entry']
            for field in required:
                if field not in data:
                    self.error(f"缺少必需字段: {field}")
                    return False
            
            # 检查工具定义
            tools = data.get('tool') or data.get('tools')
            if not tools:
                self.error("没有定义任何工具")
                return False
            
            self.success(f"YAML 格式正确，定义了 {len(tools)} 个工具")
            self.manifest_data = data
            return True
            
        except yaml.YAMLError as e:
            self.error(f"YAML 格式错误: {str(e)}")
            return False
        except Exception as e:
            self.error(f"检查失败: {str(e)}")
            return False
    
    def check_files(self):
        """检查必需文件"""
        self.step("检查必需文件")
        
        required_files = ['manifest.yaml', 'main.py', 'requirements.txt']
        all_exist = True
        
        for filename in required_files:
            filepath = self.workspace / filename
            if filepath.exists():
                self.success(f"{filename}")
            else:
                self.error(f"{filename} 不存在")
                all_exist = False
        
        return all_exist
    
    def check_python_syntax(self):
        """检查 Python 语法"""
        self.step("检查 Python 语法")
        
        python_files = ['main.py', 'plugin.py']
        all_valid = True
        
        for py_file in python_files:
            filepath = self.workspace / py_file
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    compile(content, py_file, 'exec')
                    self.success(f"{py_file} 语法正确")
                except SyntaxError as e:
                    self.error(f"{py_file} 语法错误: {e.msg} (第 {e.lineno} 行)")
                    all_valid = False
        
        return all_valid
    
    def create_package(self):
        """创建发布包"""
        self.step("创建发布包")
        
        # 确定要打包的文件
        files_to_package = [
            'manifest.yaml',
            'main.py',
            'plugin.py',
            'requirements.txt',
            'README.md',
            'icon.png'
        ]
        
        # 获取版本号
        version = self.manifest_data.get('version', '1.0.0')
        name = self.manifest_data.get('name', 'plugin')
        
        # 创建 dist 目录
        dist_dir = self.workspace / 'dist'
        dist_dir.mkdir(exist_ok=True)
        
        # 创建 ZIP 包
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"{name}_v{version}_{timestamp}.zip"
        zip_path = dist_dir / zip_filename
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename in files_to_package:
                    filepath = self.workspace / filename
                    if filepath.exists():
                        zipf.write(filepath, filename)
                        self.success(f"添加文件: {filename}")
            
            file_size = zip_path.stat().st_size / 1024
            self.success(f"创建发布包成功: {zip_filename} ({file_size:.2f} KB)")
            self.package_path = zip_path
            return True
            
        except Exception as e:
            self.error(f"创建发布包失败: {str(e)}")
            return False
    
    def update_version(self):
        """更新版本号"""
        self.step("版本管理")
        
        current_version = self.manifest_data.get('version', '1.0.0')
        self.info(f"当前版本: {current_version}")
        
        # 询问是否更新版本
        parts = str(current_version).split('.')
        if len(parts) == 3:
            major, minor, patch = parts
            new_patch = int(patch) + 1
            new_version = f"{major}.{minor}.{new_patch}"
            
            self.info(f"建议新版本: {new_version}")
            print(f"\n   是否自动升级到 {new_version}? (y/n，默认: n): ", end='')
            
            # 在自动化模式下，自动升级补丁版本
            if os.environ.get('AUTO_VERSION_BUMP') == '1':
                response = 'y'
                print('y (自动)')
            else:
                response = 'n'  # 默认不自动升级
                print('n (保持当前版本)')
            
            if response.lower() == 'y':
                # 更新 manifest.yaml
                yaml_file = self.workspace / 'manifest.yaml'
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                content = content.replace(f'version: {current_version}', f'version: {new_version}')
                
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.manifest_data['version'] = new_version
                self.success(f"版本已更新: {current_version} → {new_version}")
                return new_version
        
        return current_version
    
    def show_publish_instructions(self):
        """显示发布说明"""
        self.print_header("📦 发布说明")
        
        print(f"""
插件包已准备完成！

📦 发布包位置:
   {self.package_path}

📋 插件信息:
   名称: {self.manifest_data.get('name')}
   版本: {self.manifest_data.get('version')}
   作者: {self.manifest_data.get('author')}
   工具数: {len(self.manifest_data.get('tool', []))}

🚀 发布步骤:

1. 访问 Dify 插件市场:
   https://cloud.dify.ai

2. 点击"上传插件"或"Upload Plugin"

3. 选择发布包:
   {self.package_path.name}

4. 填写发布信息并提交

✨ 提示:
   - 确保已登录 Dify 账号
   - 首次发布可能需要审核
   - 更新版本会自动覆盖旧版本

""")
    
    def run(self):
        """执行完整流程"""
        self.print_header("🚀 Dify 插件自动发布工具")
        
        print("\n开始检测和打包流程...\n")
        
        # 1. 检查 YAML
        if not self.check_yaml():
            self.print_header("❌ 检测失败")
            print("\n请修复上述错误后重试")
            return False
        
        # 2. 检查文件
        if not self.check_files():
            self.print_header("❌ 检测失败")
            print("\n请确保所有必需文件存在")
            return False
        
        # 3. 检查语法
        if not self.check_python_syntax():
            self.print_header("❌ 检测失败")
            print("\n请修复 Python 语法错误")
            return False
        
        # 4. 版本管理
        self.update_version()
        
        # 5. 创建发布包
        if not self.create_package():
            self.print_header("❌ 打包失败")
            return False
        
        # 6. 显示发布说明
        self.show_publish_instructions()
        
        # 7. 汇总
        if self.warnings:
            self.print_header("⚠️ 警告信息")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        self.print_header("✅ 准备完成")
        print("\n插件已准备就绪，可以上传到 Dify 平台！\n")
        
        return True

if __name__ == '__main__':
    publisher = PluginPublisher()
    success = publisher.run()
    sys.exit(0 if success else 1)
