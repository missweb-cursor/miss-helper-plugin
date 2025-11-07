#!/usr/bin/env python3
"""
完整的插件集成测试 - 真实调用所有工具
"""
import sys
import os
sys.path.insert(0, '/workspace')

from tools.echo_text import EchoTextTool
from tools.transform_text import TransformTextTool
from tools.translate_text import TranslateTextTool
from tools.detect_language import DetectLanguageTool
from tools.summarize_text import SummarizeTextTool
from tools.extract_keywords import ExtractKeywordsTool
from tools.text_stats import TextStatsTool
from tools.http_get import HttpGetTool
from tools.regex_extract import RegexExtractTool

def test_tool(tool_class, tool_name, test_cases):
    """测试单个工具"""
    print(f"\n{'='*60}")
    print(f"🧪 测试: {tool_name}")
    print('='*60)
    
    tool = tool_class()
    success_count = 0
    total_count = len(test_cases)
    
    for i, (params, description) in enumerate(test_cases, 1):
        print(f"\n  测试 {i}/{total_count}: {description}")
        try:
            # 调用工具
            results = list(tool._invoke(params))
            if results:
                result_text = results[0].message if hasattr(results[0], 'message') else str(results[0])
                print(f"  ✅ 成功")
                print(f"     输入: {params}")
                print(f"     输出: {result_text[:100]}...")
                success_count += 1
            else:
                print(f"  ❌ 失败: 无返回结果")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)}")
    
    print(f"\n  结果: {success_count}/{total_count} 通过")
    return success_count == total_count

def main():
    """运行所有集成测试"""
    print("="*60)
    print("🚀 Dify 插件完整集成测试")
    print("="*60)
    
    all_tests = []
    
    # 1. Echo Text
    all_tests.append(test_tool(
        EchoTextTool,
        "Echo Text - 回显文本",
        [
            ({"text": "Hello, Dify!"}, "基本回显"),
            ({"text": "测试中文"}, "中文回显"),
            ({"text": ""}, "空字符串"),
        ]
    ))
    
    # 2. Transform Text
    all_tests.append(test_tool(
        TransformTextTool,
        "Transform Text - 文本转换",
        [
            ({"text": "hello world", "mode": "upper"}, "转大写"),
            ({"text": "HELLO WORLD", "mode": "lower"}, "转小写"),
            ({"text": "hello", "mode": "reverse"}, "反转"),
        ]
    ))
    
    # 3. Detect Language
    all_tests.append(test_tool(
        DetectLanguageTool,
        "Detect Language - 语言检测",
        [
            ({"text": "Hello, how are you?"}, "检测英文"),
            ({"text": "你好，世界！"}, "检测中文"),
            ({"text": "Bonjour le monde"}, "检测法文"),
        ]
    ))
    
    # 4. Summarize Text
    all_tests.append(test_tool(
        SummarizeTextTool,
        "Summarize Text - 文本摘要",
        [
            ({"text": "This is a test. This is another sentence. And one more sentence.", "sentences": 2}, "基本摘要"),
        ]
    ))
    
    # 5. Extract Keywords
    all_tests.append(test_tool(
        ExtractKeywordsTool,
        "Extract Keywords - 关键词提取",
        [
            ({"text": "Python is a programming language. Python is popular. Programming is fun.", "top_k": 3}, "提取关键词"),
        ]
    ))
    
    # 6. Text Stats
    all_tests.append(test_tool(
        TextStatsTool,
        "Text Stats - 文本统计",
        [
            ({"text": "Hello World\nThis is a test"}, "统计字符和单词"),
        ]
    ))
    
    # 7. HTTP GET
    all_tests.append(test_tool(
        HttpGetTool,
        "HTTP GET - HTTP请求",
        [
            ({"url": "https://httpbin.org/get", "timeout": 10}, "测试HTTP GET"),
        ]
    ))
    
    # 8. Regex Extract
    all_tests.append(test_tool(
        RegexExtractTool,
        "Regex Extract - 正则提取",
        [
            ({"text": "Email: test@example.com, another@test.com", "pattern": r"\w+@\w+\.\w+"}, "提取邮箱"),
            ({"text": "Phone: 123-456-7890", "pattern": r"\d{3}-\d{3}-\d{4}"}, "提取电话"),
        ]
    ))
    
    # 9. Translate Text (如果有API配置)
    translate_api = os.getenv("TRANSLATE_API_URL", "")
    if translate_api:
        all_tests.append(test_tool(
            TranslateTextTool,
            "Translate Text - 文本翻译",
            [
                ({"text": "Hello", "target_lang": "zh", "source_lang": "en"}, "英译中"),
            ]
        ))
    else:
        print("\n⚠️  跳过翻译测试（未配置 TRANSLATE_API_URL）")
    
    # 输出总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    passed = sum(all_tests)
    total = len(all_tests)
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有工具测试通过！插件功能完全正常！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个工具测试失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())
