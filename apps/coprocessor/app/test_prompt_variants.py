import json
import os
from typing import Any

import httpx
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Test Data ---

# 测试用的抖音视频完整文本稿
DOUYIN_TRANSCRIPT = """
说个真相啊，你相不相信你我这辈子如果不做出点改变，我们在这个社会注定只能做个牛马。是你愿意的吗？如果你愿意，那你就赶紧划走。如果你和我一样不认命不愿意，那请你耐心听完这段视频，我会告诉你问题出在哪里，也会告诉你我们需要做出什么改变。各位上学的时候，谁不知道好好读书就能上个好大学，找个好工作。但六年的小学，三年的初中，外加三年的高中，整整12年啊。如果让你天天刷题看书不留号，你能做到吗？你没有做到。所以能考上好大学的永远是少数人。好，我们工作了谁不知道，只要多花时间，多钻研业务，多跑客户，就能升职加薪。可看到别人到点了就下班，你加不加班？别人周末躺平了你学不学习？别人假期带着家人孩子去旅游度假了，你告诉我你能不能静下心来研究方案。好，假如你说你能，那让你坚持十年二十年，你还说你能吗？你不能。所以这种日复一日筛掉了很多心高气傲。好，我们年纪大了，医生告诉你，只要你能管住嘴，迈开腿，身体就能健康。可是又有多少人能忍得住不吃香的不喝辣的，又有多少人能雷打不动的每天坚持跑步1小时？听出来了吗？这跟人性的即时满足本能是对着干的，它会让人一点都不舒服。但学习、工作、健康，你想做好就得跟着人性反着来，这就是问题的核心。人性让我们在每个阶段都很难聚焦，我们的时间精力太容易被那些碎片化的诱惑给分散了。就像今天早晨，我明明计划要做一个重要的ppt，结果呢微信发了个没完，抖音一刷就停不下来，一抬头一上午已经没有了。我们每个人真正用在学习、工作、健康上的时间，我们算一算是不是少的可怜。时间精力的分散就是我们大多数人拿不到结果的根本原因。而真正能拿到大结果的人都选择了延迟满足，都是对抗人性的高手。老铁们，你我都不想做牛马人上人这条路很窄，因为它反人性，它违背了我们贪图舒服的本能，所以它注定艰难，但这是我们唯一的捷径。李哥送你一句话，难走的路从不拥挤，反人性的坚持才是普通人的捷径。
"""

# 原始 Prompt (从文件中读取)
with open("app/prompts/structured_analysis.prompt") as f:
    ORIGINAL_PROMPT_TEMPLATE = f.read()

# 从原始 prompt 中提取配置
ORIGINAL_PROMPT_CONFIG = json.loads(ORIGINAL_PROMPT_TEMPLATE)

# 优化后的 Prompt（语言自适应 + Clean and Analyze 两步法）2.2
PROMPT_OPTIMIZED_CONFIG = {
    "prompt_instruction": "You are an expert in analyzing video transcripts for content strategy. Your task is to perform a two-step 'Clean and Analyze' process based on the user-provided raw transcript. Respond ONLY with a valid JSON object in the following format, with no additional explanations. You MUST respond in the same language as the input transcript.",
    "output_format": {
        "raw_transcript": "The original, untouched user-provided transcript.",
        "cleaned_transcript": "A cleaned, analysis-ready version of the transcript. You MUST: 1. [Noise Reduction]: Remove filler words (e.g., '嗯', '啊', '这个', '那个', '就是说'). 2. [Trimming]: Remove standard greetings/closings (e.g., '大家好我是...', '欢迎收看...', '点赞关注', '感谢三连'). 3. [Re-chunking]: Add logical paragraph breaks ('\\n\\n') based on semantic meaning to fix the 'wall of text' issue and improve readability.",
        "analysis": {
            "hook": "[Based ONLY on the cleaned_transcript] The first 1-3 sentences that grab the viewer's attention.",
            "core": "[Based ONLY on the cleaned_transcript] First, determine the central topic or purpose of the video. Then, extract the main statement or conclusion related to that purpose. Finally, list up to two essential pieces of evidence, steps, or examples provided to support this main statement. Keep the summary focused and distinct from the hook/cta.",
            "cta": "[Based ONLY on the cleaned_transcript] The final sentence(s) that call the viewer to take a specific action (e.g., like, follow, comment).",
        },
    },
}


def build_system_prompt(config: dict) -> str:
    """构建 system prompt"""
    instruction = config.get("prompt_instruction", "")
    output_format = config.get("output_format", {})

    if instruction:
        return f"{instruction}\n\n{json.dumps(output_format, indent=2, ensure_ascii=False)}"
    else:
        # 兼容旧格式
        return json.dumps(output_format, indent=2, ensure_ascii=False)


async def call_llm_with_prompt(config: dict, transcript: str) -> dict[str, Any]:
    """调用 LLM API 进行分析"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set")

    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    system_prompt = build_system_prompt(config)

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript},
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
        )

        response.raise_for_status()
        result = response.json()

        # 提取响应内容
        content = result["choices"][0]["message"]["content"]

        # 去掉 markdown 代码块标记
        cleaned_content = content.strip()
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]
        cleaned_content = cleaned_content.strip()

        # 解析 JSON
        return json.loads(cleaned_content)


def print_analysis_result(prompt_name: str, result: dict[str, Any]) -> None:
    """格式化打印分析结果"""
    print(f"\n{'='*80}")
    print(f"Prompt: {prompt_name}")
    print(f"{'='*80}")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"{'='*80}\n")


def compare_results(original: dict[str, Any], optimized: dict[str, Any]) -> None:
    """对比两个 prompt 的结果"""
    print(f"\n{'#'*80}")
    print("结果对比分析")
    print(f"{'#'*80}\n")

    # 1. 输出结构对比
    print("【1. 输出结构对比】")
    print(f"  Original Keys: {list(original.keys())}")
    print(f"  Optimized Keys: {list(optimized.keys())}")
    print()

    # 2. Hook 对比
    print("【2. Hook (开场) 对比】")
    original_hook = original.get("hook") or original.get("analysis", {}).get("hook")
    optimized_hook = optimized.get("analysis", {}).get("hook")
    print(f"  Original:  {original_hook}")
    print(f"  Optimized: {optimized_hook}")
    print()

    # 3. Core (核心内容) 对比
    print("【3. Core (核心内容) 对比】")
    original_core = original.get("core") or original.get("analysis", {}).get("core")
    optimized_core = optimized.get("analysis", {}).get("core")
    print(f"  Original:\n    {original_core}")
    print(f"  Optimized:\n    {optimized_core}")
    print()

    # 4. CTA (行动号召) 对比
    print("【4. CTA (行动号召) 对比】")
    original_cta = original.get("cta") or original.get("analysis", {}).get("cta")
    optimized_cta = optimized.get("analysis", {}).get("cta")
    print(f"  Original:  {original_cta}")
    print(f"  Optimized: {optimized_cta}")
    print()

    # 5. 优化版特有功能
    if "cleaned_transcript" in optimized:
        print("【5. 优化版特有功能 - 文本清洗】")
        print(f"  Raw Transcript Length: {len(optimized.get('raw_transcript', ''))}")
        print(f"  Cleaned Transcript Length: {len(optimized.get('cleaned_transcript', ''))}")
        print("  Cleaned Transcript Preview (前200字符):")
        cleaned_preview = optimized.get('cleaned_transcript', '')[:200]
        print(f"    {cleaned_preview}...")
        print()

    # 6. 总结
    print("【6. 分析总结】")
    print("  - 原始版本: 直接从原文提取三段式结构")
    print("  - 优化版本: 先清洗文本，再基于清洗后的文本进行结构化分析")
    print("  - 优化点: 1) 去除语气词和无效内容 2) 语义分段 3) 提高可读性")
    print(f"\n{'#'*80}\n")


# --- Test Cases ---


@pytest.mark.asyncio
async def test_original_prompt():
    """测试原始 Prompt"""
    print("\n" + "="*80)
    print("测试 1/2: 原始 Prompt")
    print("="*80)

    result = await call_llm_with_prompt(ORIGINAL_PROMPT_CONFIG, DOUYIN_TRANSCRIPT)
    print_analysis_result("Original", result)

    # 基本断言
    assert isinstance(result, dict)
    # 兼容两种格式
    if "analysis" in result:
        assert "hook" in result["analysis"]
        assert "core" in result["analysis"]
        assert "cta" in result["analysis"]
    else:
        assert "hook" in result
        assert "core" in result
        assert "cta" in result

    return result


@pytest.mark.asyncio
async def test_optimized_prompt():
    """测试优化后的 Prompt"""
    print("\n" + "="*80)
    print("测试 2/2: 优化后的 Prompt")
    print("="*80)

    result = await call_llm_with_prompt(PROMPT_OPTIMIZED_CONFIG, DOUYIN_TRANSCRIPT)
    print_analysis_result("Optimized", result)

    # 基本断言
    assert isinstance(result, dict)
    assert "raw_transcript" in result
    assert "cleaned_transcript" in result
    assert "analysis" in result
    assert "hook" in result["analysis"]
    assert "core" in result["analysis"]
    assert "cta" in result["analysis"]

    # 验证清洗功能
    assert len(result["cleaned_transcript"]) > 0
    assert result["raw_transcript"] != result["cleaned_transcript"]

    return result


@pytest.mark.asyncio
async def test_compare_prompts():
    """对比两个 Prompt 的效果"""
    print("\n" + "="*80)
    print("开始对比测试")
    print("="*80)

    # 调用两个 prompt
    original_result = await call_llm_with_prompt(
        ORIGINAL_PROMPT_CONFIG, DOUYIN_TRANSCRIPT
    )
    optimized_result = await call_llm_with_prompt(
        PROMPT_OPTIMIZED_CONFIG, DOUYIN_TRANSCRIPT
    )

    # 打印结果
    print_analysis_result("Original", original_result)
    print_analysis_result("Optimized", optimized_result)

    # 对比分析
    compare_results(original_result, optimized_result)


"""
如何运行这个测试:

1. 确保您的 `.env` 文件中已配置好有效的 LLM API 密钥:
   DEEPSEEK_API_KEY=your_api_key_here

2. 在 `apps/coprocessor` 目录下，激活虚拟环境并运行 pytest:

   # 运行所有测试
   pytest app/test_prompt_variants.py -sv

   # 只运行对比测试
   pytest app/test_prompt_variants.py::test_compare_prompts -sv

   # 只运行单个测试
   pytest app/test_prompt_variants.py::test_original_prompt -sv
   pytest app/test_prompt_variants.py::test_optimized_prompt -sv

3. 参数说明:
   -s: 显示 print 输出
   -v: 显示详细信息

4. 观察输出结果，重点关注:
   - 原始版本和优化版本的结构差异
   - cleaned_transcript 的清洗效果
   - hook/core/cta 的提取质量差异
"""
