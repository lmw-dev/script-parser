import json
import os

import pytest
from dotenv import load_dotenv
from app.http_client import get_http_client
from app.services.llm_service import DeepSeekAdapter

# Load environment variables
load_dotenv()

# --- Test Data ---

# 测试用的抖音视频完整文本稿
DOUYIN_TRANSCRIPT = """
买了原装或者是平替妙控键盘，但只会用来打字的豹子们，保姆级教程收好不屑。收到妙控键盘以后，第一件事到设置里搜索触控板，把轻点一点按打开，这样每次点击就不用费力的去按触控板了。记得把触控板也调到喜欢的速度，这样用起来才会更熟。设置辅助功能，指针控制里可以对指针进行进一步的设置，这些选项全都可以试一试，颜色、大小、圆圈的粗细都可以调节，点右上角可以调出控制中心，挪到底部以后再往下一滑能调出do栏再编辑文字的界面，轻点两下是选中字词，轻点3下是选中整段。还有一个技巧很少人知道，选中一个字词以后，按住shift键再搭配上下左右键，就可以一起选中这个字词附近的文字。两根手指上下滑动是滚动页面，左右移动是前进或后退，两根手指对角线方向移动。除了可以放大缩小界面以外，看视频的时候也可以用来打开全屏或者退出全屏。这个是我最近才发现的，非常好用。三根手指左右滑，能在最近用过的app当中来回切换。三根手指潇洒的向上滑是回到桌面，三根手指犹豫不决的向上滑，可以看到多任务界面，然后再用两根手指向下滑，就是关闭后台运行。记不住没关系啊，你上手直接这么划屏幕也是很方便的。Command加C是复制，加V粘贴加X剪切加C撤销，shift加common加3或4都是截屏。Command加tap可以在已打开的app里面快速切换浏览器里shift加common加左右中括号是切换标签页，按地图键可以切换输入法，其中以摸迹表情也在这里。不同的app快捷键不一样，长按comm键都可以看到，把常用的记忆记就行了。如果要在打字和手写两种形态之间来回切换，反复拆装iPad就会很麻烦。这个时候我们就可以把妙控整个倒过来，这个角度刚好可以写字，只要控制好力度，尽量写在屏幕的下半部分，就不容易塌下去。大家应该知道，原装调控是通过I pad背后的三个金属点直接跟iPad连接的，键盘耗的是I pad的电量，所以转轴上的这个充电口自然也是给I pad充电用的了。虽然说这个口充电会比较慢，但好处就是I pad自身的充电口就可以用来插拓展物优盘什么的还是非常必要的。在光线不足的环境里，原装妙控会自动开启键盘背光。如果你觉得不够亮，可以到设置键盘实体键盘里拉动这个滑杆。注意哦光线充足的时候，这个拉杆是拉不动的，并不是你的妙控键盘坏了。最后一个技巧，如果你觉得这种悬浮式的键盘呢保护不到iPad的侧面，pencil还容易掉，那可以去入一个这种伴侣壳，摘下来还能搭配双面夹使用。我上周刚送了我爸一个，他很喜欢。详细的测评视频可以参考这一期。
"""

# 原始 Prompt (从文件中读取)
with open("app/prompts/structured_analysis.prompt") as f:
    ORIGINAL_PROMPT_TEMPLATE = f.read()

# 从原始 prompt 中提取 JSON 部分
def extract_instructions_from_prompt(prompt_text: str) -> dict:
    """从 prompt 文本中提取 JSON 指令"""
    try:
        # 尝试找到 JSON 部分
        # 方法1: 从文件内容中找到包含 JSON 的部分
        if '{' in prompt_text and '}' in prompt_text:
            start_idx = prompt_text.find('{')
            end_idx = prompt_text.rfind('}') + 1
            json_part = prompt_text[start_idx:end_idx]
            return json.loads(json_part)
        else:
            # 如果没有找到 JSON，返回默认结构
            return {
                "hook": "The first 1-3 sentences that grab the viewer's attention.",
                "core": "The main body of the content, summarizing the key points.",
                "cta": "The final sentence(s) that call the viewer to take a specific action (e.g., like, follow, comment)."
            }
    except (json.JSONDecodeError, ValueError):
        # 如果解析失败，返回默认结构
        return {
            "hook": "The first 1-3 sentences that grab the viewer's attention.",
            "core": "The main body of the content, summarizing the key points.",
            "cta": "The final sentence(s) that call the viewer to take a specific action (e.g., like, follow, comment)."
        }

# 提取原始 prompt 的指令
ORIGINAL_PROMPT_INSTRUCTIONS = extract_instructions_from_prompt(ORIGINAL_PROMPT_TEMPLATE)

# 变体 A (强调中心思想)
PROMPT_VARIANT_A = {
    "hook": "The first 1-3 sentences that grab the viewer's attention.",
    "core": "Identify the single most important message, argument, or value proposition the speaker wants to convey. Summarize this core idea concisely, potentially including 1-2 key supporting points or examples mentioned in the main body. Exclude introductory hooks and concluding calls to action.",
    "cta": "The final sentence(s) that call the viewer to take a specific action (e.g., like, follow, comment)."
}

# 变体 B (结构化引导)
PROMPT_VARIANT_B = {
    "hook": "The first 1-3 sentences that grab the viewer's attention.",
    "core": "First, determine the central topic or purpose of the video. Then, extract the main statement or conclusion related to that purpose. Finally, list up to two essential pieces of evidence, steps, or examples provided to support this main statement. Keep the summary focused and distinct from the hook/cta. IMPORTANT: You must respond in Chinese (简体中文).",
    "cta": "The final sentence(s) that call the viewer to take a specific action (e.g., like, follow, comment)."
}

# 变体 C (Few-shot 示例)
PROMPT_VARIANT_C = {
    "hook": "The first 1-3 sentences that grab the viewer's attention.",
    "core": "Analyze the main body to find the core message. It should explain the central 'what' and 'why' or 'how'. Similar to these examples: [Example 1 Core Text], [Example 2 Core Text]. Extract the core message and its 1-2 main supporting details from the provided transcript. IMPORTANT: You must respond in Chinese (简体中文).",
    "cta": "The final sentence(s) that call the viewer to take a specific action (e.g., like, follow, comment)."
}

# 优化后的 Prompt（语言自适应 + 结构化引导）
PROMPT_OPTIMIZED = {
    "hook": "The first 1-3 sentences that grab the viewer's attention.",
    "core": "First, determine the central topic or purpose of the video. Then, extract the main statement or conclusion related to that purpose. Finally, list up to two essential pieces of evidence, steps, or examples provided to support this main statement. Keep the summary focused and distinct from the hook/cta.",
    "cta": "The final sentence(s) that call the viewer to take a specific action (e.g., like, follow, comment)."
}

# 优化的 system prompt
def build_optimized_prompt():
    """构建优化后的 prompt"""
    prompt_instruction = """You are an expert in analyzing video transcripts. Your task is to extract the core structure of the content based on the user-provided transcript. You must identify three key parts: the Hook, the Core, and the Call to Action (CTA). Respond ONLY with a valid JSON object in the following format, with no additional explanations. You MUST respond in the same language as the input transcript."""
    return prompt_instruction

def build_prompt(template, instructions):
    """辅助函数，用于将新的指令注入到原始模板中"""
    # 构建完整的 prompt
    prompt_intro = """You are an expert in analyzing video transcripts. Your task is to extract the core structure of the content based on the user-provided transcript.
Respond ONLY with a valid JSON object in the following format, with no additional explanations:"""

    return f"{prompt_intro}\n{json.dumps(instructions, indent=2)}"


# --- Test Cases ---

@pytest.mark.parametrize(
    "prompt_name, prompt_instructions, use_optimized_prompt",
    [
        ("Original", ORIGINAL_PROMPT_INSTRUCTIONS, False),
        ("Variant_A", PROMPT_VARIANT_A, False),
        ("Variant_B", PROMPT_VARIANT_B, False),
        ("Variant_C", PROMPT_VARIANT_C, False),
        ("Optimized", PROMPT_OPTIMIZED, True),
    ],
)
@pytest.mark.asyncio
async def test_prompt_variants_for_structured_analysis(prompt_name, prompt_instructions, use_optimized_prompt):
    """
    测试不同的prompt变体对抖音脚本的结构化分析效果。
    这个测试会调用真实的LLM服务，用于评估和对比结果。
    """
    print(f"\n--- Testing Prompt: {prompt_name} ---")

    # 1. Arrange
    # 构建最终的prompt - 这里我们需要创建一个自定义的 prompt 来测试不同的变体
    # 注意：这将进行真实的API调用，请确保您的环境已配置API密钥

    client = None
    try:
        # 为这个测试创建一个修改过的 prompt
        # 这里我们需要直接调用底层 API，因为我们想测试不同的 prompt 指令

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            pytest.skip("DEEPSEEK_API_KEY not set, skipping test")

        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

        # 构建完整的 prompt
        if use_optimized_prompt:
            # 使用优化后的 system prompt
            system_prompt = build_optimized_prompt()
            # 提取 output_format
            output_format = json.dumps(prompt_instructions, indent=2)
            system_prompt = f"{system_prompt}\n{output_format}"
        else:
            # 使用标准的 build_prompt 函数
            system_prompt = build_prompt(ORIGINAL_PROMPT_TEMPLATE, prompt_instructions)

        # 2. Act - 调用LLM进行分析
        # 使用同步的 httpx 客户端避免事件循环问题
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                        {"role": "user", "content": DOUYIN_TRANSCRIPT},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000,
                },
            )

            response.raise_for_status()
            result = response.json()

            # 提取响应内容
            content = result["choices"][0]["message"]["content"]
            
            # 去掉 markdown 代码块标记
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]  # 移除 ```json
            elif cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]  # 移除 ```
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]  # 移除末尾的 ```
            cleaned_content = cleaned_content.strip()

            # 尝试解析结果为JSON
            analysis_json = json.loads(cleaned_content)

            # 打印结果用于手动比对
            print(f"Prompt ({prompt_name}) Analysis Result:")
            print(json.dumps(analysis_json, indent=2, ensure_ascii=False))

            # 3. Assert
            # 基本断言：确保返回的是一个包含预期键的字典
            assert isinstance(analysis_json, dict)
            assert "hook" in analysis_json
            assert "core" in analysis_json
            assert "cta" in analysis_json

    except json.JSONDecodeError as e:
        print(f"Result for {prompt_name} is not valid JSON:")
        if 'result' in locals():
            print(result)
        pytest.fail(f"LLM response for {prompt_name} was not valid JSON: {e}")
    except Exception as e:
        print(f"Error for {prompt_name}: {type(e).__name__}: {e}")
        raise

"""
如何运行这个测试:
1.  将抖音视频的文本稿粘贴到 `DOUYIN_TRANSCRIPT` 变量中。
2.  确保您的 `.env` 文件中已配置好有效的 LLM API 密钥。
3.  在 `apps/coprocessor` 目录下，激活虚拟环境并运行 pytest:
    source .venv/bin/activate
    pytest app/test_prompt_variants.py -sv
    (-s 会显示print输出, -v 提供详细信息)
4.  观察每个 prompt 变体的输出结果，进行比较。
"""
