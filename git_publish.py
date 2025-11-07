#!/usr/bin/env python3
"""
Git 仓库插件发布脚本
为 Dify 从代码仓库安装插件做准备
"""
import os
import sys
import yaml
import subprocess
from pathlib import Path

class GitPluginPublisher:
    def __init__(self):
        self.workspace = Path('/workspace')
        self.errors = []
        self.warnings = []
        
    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)
    
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
    
    def run_command(self, cmd, description=None):
        """执行命令"""
        if description:
            self.info(description)
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                cwd=self.workspace,
                capture_output=True, 
                text=True,
                check=False
            )
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
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
            
            self.success(f"YAML 格式正确")
            self.info(f"插件名称: {data.get('name')}")
            self.info(f"版本: {data.get('version')}")
            self.info(f"工具数: {len(tools)}")
            
            self.manifest_data = data
            return True
            
        except yaml.YAMLError as e:
            self.error(f"YAML 格式错误: {str(e)}")
            return False
        except Exception as e:
            self.error(f"检查失败: {str(e)}")
            return False
    
    def check_git_status(self):
        """检查 Git 状态"""
        self.step("检查 Git 仓库状态")
        
        # 检查是否是 Git 仓库
        success, stdout, stderr = self.run_command("git rev-parse --git-dir")
        if not success:
            self.error("当前目录不是 Git 仓库")
            return False
        
        self.success("Git 仓库已初始化")
        
        # 获取当前分支
        success, branch, _ = self.run_command("git branch --show-current")
        if success and branch.strip():
            self.info(f"当前分支: {branch.strip()}")
            self.current_branch = branch.strip()
        
        # 获取远程仓库
        success, remote, _ = self.run_command("git remote -v")
        if success and remote.strip():
            lines = remote.strip().split('\n')
            if lines:
                # 提取仓库 URL
                parts = lines[0].split()
                if len(parts) >= 2:
                    repo_url = parts[1]
                    # 清理 URL，移除 token
                    if '@github.com' in repo_url:
                        repo_url = 'https://github.com/' + repo_url.split('@github.com/')[-1]
                    self.info(f"远程仓库: {repo_url}")
                    self.repo_url = repo_url
        
        # 检查是否有未提交的更改
        success, status, _ = self.run_command("git status --porcelain")
        if success:
            if status.strip():
                self.warning("有未提交的更改")
                self.info("运行 'git status' 查看详情")
                return True
            else:
                self.success("工作区干净，没有未提交的更改")
        
        return True
    
    def get_installation_url(self):
        """获取安装 URL"""
        self.step("生成安装信息")
        
        if not hasattr(self, 'repo_url'):
            self.error("无法获取仓库 URL")
            return False
        
        # 生成不同的安装方式
        self.success("插件安装方式：")
        
        print("\n   📍 方式 1: 使用仓库 URL + 分支")
        print(f"      仓库: {self.repo_url}")
        print(f"      分支: {self.current_branch}")
        
        print("\n   📍 方式 2: 使用完整 Git URL")
        full_url = f"{self.repo_url}#branch={self.current_branch}"
        print(f"      {full_url}")
        
        print("\n   📍 方式 3: 使用主分支（如果已合并）")
        print(f"      {self.repo_url}")
        
        return True
    
    def show_dify_instructions(self):
        """显示 Dify 安装说明"""
        self.print_header("📦 Dify 插件安装说明")
        
        print(f"""
您的插件已准备完成！现在可以在 Dify 中安装了。

📋 插件信息:
   名称: {self.manifest_data.get('name')}
   版本: {self.manifest_data.get('version')}
   作者: {self.manifest_data.get('author')}
   工具数: {len(self.manifest_data.get('tool', []))}

🚀 在 Dify 中安装插件的步骤:

1. 登录 Dify 平台
   https://cloud.dify.ai

2. 进入插件管理页面
   - 点击左侧菜单的 "Plugins" 或 "插件"
   - 点击 "Install from GitHub" 或 "从 GitHub 安装"

3. 输入仓库信息
   仓库 URL: {self.repo_url}
   分支: {self.current_branch}

4. 点击"安装"并等待完成

📝 注意事项:
   ✓ 确保仓库是公开的，或者 Dify 有访问权限
   ✓ manifest.yaml 必须在仓库根目录
   ✓ 确保所有依赖在 requirements.txt 中声明
   ✓ 如有更新，在 Dify 中点击"更新"即可获取最新版本

🔧 如需更新插件:
   1. 修改代码和 manifest.yaml (更新版本号)
   2. 提交并推送到 Git 仓库
   3. 在 Dify 插件管理中点击"更新"

⚡ 快速命令:
   # 检查插件
   python3 check_plugin.py
   
   # 准备发布
   python3 git_publish.py
   
   # 查看 Git 状态
   git status
""")
    
    def run(self):
        """执行完整流程"""
        self.print_header("🚀 Git 仓库插件发布工具")
        
        print("\n为 Dify 从代码仓库安装做准备...\n")
        
        # 1. 检查 YAML
        if not self.check_yaml():
            self.print_header("❌ 检测失败")
            print("\n请修复 manifest.yaml 的错误")
            return False
        
        # 2. 检查 Git 状态
        if not self.check_git_status():
            self.print_header("❌ Git 检查失败")
            return False
        
        # 3. 获取安装 URL
        if not self.get_installation_url():
            self.print_header("❌ 无法生成安装信息")
            return False
        
        # 4. 显示 Dify 安装说明
        self.show_dify_instructions()
        
        # 5. 汇总警告
        if self.warnings:
            self.print_header("⚠️ 警告信息")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        self.print_header("✅ 准备完成")
        print("\n插件已准备就绪，可以在 Dify 中通过 Git 仓库安装！\n")
        
        return True

if __name__ == '__main__':
    publisher = GitPluginPublisher()
    success = publisher.run()
    sys.exit(0 if success else 1)
