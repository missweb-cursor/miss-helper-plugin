#!/usr/bin/env python3
"""
完整的插件发布检查脚本
包含 YAML、文件、环境配置等全面检查
"""
import os
import sys
import yaml
from pathlib import Path

class CompletePluginChecker:
    def __init__(self):
        self.workspace = Path('/workspace')
        self.errors = []
        self.warnings = []
        
    def print_header(self, title):
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def step(self, msg):
        print(f"\n🔹 {msg}")
    
    def success(self, msg):
        print(f"   ✅ {msg}")
    
    def error(self, msg):
        print(f"   ❌ {msg}")
        self.errors.append(msg)
    
    def warning(self, msg):
        print(f"   ⚠️  {msg}")
        self.warnings.append(msg)
    
    def info(self, msg):
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
            missing = []
            for field in required:
                if field not in data:
                    missing.append(field)
            
            if missing:
                self.error(f"缺少必需字段: {', '.join(missing)}")
                return False
            
            # 检查重复键（通过文本检查）
            lines = content.split('\n')
            top_level_keys = {}
            for i, line in enumerate(lines, 1):
                stripped = line.lstrip()
                if stripped and not stripped.startswith('#') and ':' in stripped:
                    if line and line[0] not in [' ', '\t', '-']:
                        key = stripped.split(':')[0].strip()
                        if key in top_level_keys:
                            self.error(f"第 {i} 行: 键 '{key}' 重复（首次出现在第 {top_level_keys[key]} 行）")
                            return False
                        else:
                            top_level_keys[key] = i
            
            # 检查工具定义
            tools = data.get('tool') or data.get('tools')
            if not tools:
                self.error("没有定义任何工具")
                return False
            
            self.success("YAML 格式正确")
            self.info(f"插件: {data.get('name')} v{data.get('version')}")
            self.info(f"工具数: {len(tools)}")
            
            self.manifest_data = data
            return True
            
        except yaml.YAMLError as e:
            self.error(f"YAML 格式错误: {str(e)}")
            return False
        except Exception as e:
            self.error(f"检查失败: {str(e)}")
            return False
    
    def check_env_files(self):
        """检查环境配置文件"""
        self.step("检查环境配置")
        
        env_example = self.workspace / '.env.example'
        env_file = self.workspace / '.env'
        gitignore = self.workspace / '.gitignore'
        
        # 检查 .env.example
        if env_example.exists():
            self.success(".env.example 存在（配置模板）")
        else:
            self.warning(".env.example 不存在（建议提供配置模板）")
        
        # 检查 .env 是否被忽略
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                gitignore_content = f.read()
            if '.env' in gitignore_content:
                self.success(".env 已在 .gitignore 中（安全）")
            else:
                self.warning(".env 未在 .gitignore 中（可能泄露敏感信息）")
        
        # 检查 .env 是否存在（不应该提交）
        if env_file.exists():
            self.warning(".env 文件存在（确保不要提交到 Git）")
            self.info("本地开发使用，但不应推送到远程仓库")
        else:
            self.info(".env 文件不存在（从 .env.example 复制以进行本地开发）")
        
        return True
    
    def check_required_files(self):
        """检查必需文件"""
        self.step("检查必需文件")
        
        required = {
            'manifest.yaml': '插件配置',
            'main.py': '主入口',
            'requirements.txt': '依赖声明'
        }
        
        optional = {
            'plugin.py': '插件实现',
            'README.md': '说明文档',
            'icon.png': '插件图标',
            '.env.example': '配置模板',
            '.gitignore': 'Git 忽略规则'
        }
        
        all_exist = True
        for filename, desc in required.items():
            filepath = self.workspace / filename
            if filepath.exists():
                self.success(f"{filename} - {desc}")
            else:
                self.error(f"{filename} 缺失 - {desc}")
                all_exist = False
        
        print()
        for filename, desc in optional.items():
            filepath = self.workspace / filename
            if filepath.exists():
                self.info(f"{filename} - {desc}")
        
        return all_exist
    
    def check_git_status(self):
        """检查 Git 状态"""
        self.step("检查 Git 仓库")
        
        import subprocess
        
        try:
            # 检查是否是 Git 仓库
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.warning("不是 Git 仓库（无法从 Git 安装）")
                return False
            
            self.success("Git 仓库已初始化")
            
            # 获取当前分支
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                branch = result.stdout.strip()
                self.info(f"当前分支: {branch}")
                self.current_branch = branch
            
            # 获取远程仓库
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                url = result.stdout.strip()
                # 清理 URL
                if '@github.com' in url:
                    url = 'https://github.com/' + url.split('@github.com/')[-1].replace('.git', '')
                self.info(f"远程仓库: {url}")
                self.repo_url = url
            
            # 检查工作区状态
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.workspace,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                if result.stdout.strip():
                    self.warning("有未提交的更改")
                else:
                    self.success("工作区干净")
            
            return True
            
        except Exception as e:
            self.warning(f"Git 检查失败: {str(e)}")
            return False
    
    def show_install_instructions(self):
        """显示安装说明"""
        self.print_header("🚀 在 Dify 中安装此插件")
        
        print(f"""
📋 插件信息:
   名称: {self.manifest_data.get('name')}
   版本: {self.manifest_data.get('version')}
   作者: {self.manifest_data.get('author')}
   工具数: {len(self.manifest_data.get('tool', []))}

🔗 安装方式:

1. 登录 Dify 云平台
   https://cloud.dify.ai

2. 进入插件管理
   导航: 工作区设置 → 插件 → 安装插件

3. 选择安装方式
   方式 A: 从 GitHub 安装（推荐）
      - 仓库 URL: {getattr(self, 'repo_url', 'https://github.com/missweb-cursor/miss-helper-plugin')}
      - 分支: {getattr(self, 'current_branch', 'main')}
   
   方式 B: 从 Marketplace 安装
      - 搜索插件名称
      - 点击安装

📝 环境变量配置（可选）:
   如需配置插件，在 Dify 插件设置中添加环境变量：
   - PUBLISH_TOKEN: API 鉴权令牌
   - TRANSLATE_API_URL: 翻译服务地址
   - TRANSLATE_API_KEY: 翻译服务密钥

💡 提示:
   ✓ 插件会自动从 Git 仓库同步
   ✓ 更新代码后，在 Dify 中点击"更新"
   ✓ 确保 manifest.yaml 在仓库根目录
   ✓ 依赖会自动从 requirements.txt 安装

""")
    
    def run(self):
        """执行完整检查"""
        self.print_header("🔍 Dify 插件完整性检查")
        
        # 1. 检查 YAML
        if not self.check_yaml():
            self.print_header("❌ 检查失败")
            print("\n请修复 manifest.yaml 的错误")
            return False
        
        # 2. 检查必需文件
        if not self.check_required_files():
            self.print_header("❌ 检查失败")
            print("\n请确保所有必需文件存在")
            return False
        
        # 3. 检查环境配置
        self.check_env_files()
        
        # 4. 检查 Git 状态
        self.check_git_status()
        
        # 5. 显示安装说明
        self.show_install_instructions()
        
        # 6. 汇总
        if self.warnings:
            self.print_header("⚠️ 警告信息")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
            print()
        
        if self.errors:
            self.print_header("❌ 错误信息")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
            print()
            return False
        
        self.print_header("✅ 检查完成")
        print("\n插件已准备就绪，可以在 Dify 中通过 Git 仓库安装！\n")
        
        return True

if __name__ == '__main__':
    checker = CompletePluginChecker()
    success = checker.run()
    sys.exit(0 if success else 1)
