import os
import requests
from datetime import datetime

# 通过 GitHub Secrets 注入的环境变量
WEBHOOK = os.environ["WECHAT_WEBHOOK"]
XAI_API_KEY = os.environ["XAI_API_KEY"]

URL = "https://api.x.ai/v1/chat/completions"

# 构造优化版提示词
now_str = datetime.now().strftime('%Y年%m月%d日 %H:%M')
prompt = (
    f"现在北京时间{now_str}，请按以下要求生成化工行业情报：\n\n"
    "你是一名熟悉中国煤化工和大宗商品市场的研究员，现在请基于最新可获得的公开信息，"
    '撰写一份"液氨、甲醇、尿素、氢气、硫磺、三聚氰胺、天然气"的日度行业情报简报。\n'
    "要求：\n"
    "1. 必须优先使用真实、可公开验证的来源（交易所、龙头企业公告、行业协会、主流资讯网站等），禁止编造数据或来源。\n"
    '2. 若某项数据在最近3天内没有可靠公开数据,请明确写"暂无可靠公开数据"，不要猜测。\n'
    "3. 报告结构请使用 Markdown，严格按以下顺序输出：\n\n"
    "## 一、整体概览（100字以内）\n"
    "- 用1–3句话概括当日煤化工链条整体价格走势、开工变化和主要风险点。\n\n"
    "## 二、品种跟踪\n"
    "按液氨、甲醇、尿素、氢气、硫磺、三聚氰胺、天然气的顺序，每个品种输出一个小节：\n"
    "### 品种名称\n"
    "- 价格：主流地区现货/期货价格区间（含币种、单位），与上一交易日或上周的涨跌幅；注明数据日期和来源简称。\n"
    "- 开工率：代表性开工率或装置负荷（注明口径）；若无数据则说明。\n"
    "- 库存：代表性库存数据；若无数据则说明。\n"
    "- 检修与供给变化：重要装置检修、复产、新投产信息，给出规模、起始日期、预计持续时间和来源。\n"
    "- 需求与下游观察：主要下游行业的开工、订单或需求变化（只写事实，不写主观预测）。\n\n"
    "## 三、生产安全事故情况（化工行业）\n"
    "- 汇总最近24小时中国及全球重要化工生产安全事故：时间、地点、涉及品种/装置类型、伤亡/停产影响、简要原因（如已知）、信息来源链接。\n"
    '- 若最近24小时无重大事故，请写"最近24小时未发现重大公开报道的化工生产安全事故"。\n\n'
    "## 四、环保管控及政策动态\n"
    "- 列举最近3天内与化工及相关产业链有关的环保管控、排放标准、能耗双控、产能置换、进出口关税/配额、补贴或税收政策等变动。\n"
    "- 每条说明：发布日期、发布机构、政策要点（不超过两句）、涉及品种/地区、原文或权威解读链接。\n\n"
    "## 五、套利与风险提示（简要）\n"
    '- 基于上述已确认的价格和供需事实，列出不超过3条可能的价差/套利机会或风险点，用条件句表述，不做具体投资建议，并注明"仅供行业参考，不构成投资建议"。\n\n'
    "## 六、数据来源与可靠性说明\n"
    "- 列出本次引用的主要数据来源及对应国家或地区。\n"
    "- 提醒数据可能存在滞后、抽样口径不同等限制。\n\n"
    "4. 全文控制在约1000字以内，优先保证关键数据和来源说明，句子尽量短，不要夸张修饰。\n"
    '5. 遇到不确定的信息时，用"尚无公开一致结论"或"不同来源存在分歧"描述，并说明大致分歧方向，不要强行下结论。'
)

# 调用 x.ai 生成情报
payload = {
    "model": "grok-3",
    "temperature": 0.2,
    "max_tokens": 1000,  # 控制生成长度，大约千字左右
    "messages": [
        {"role": "user", "content": prompt}
    ],
}

headers = {
    "Authorization": f"Bearer {XAI_API_KEY}",
    "Content-Type": "application/json",
}

resp = requests.post(URL, json=payload, headers=headers, timeout=40)
print("x.ai status:", resp.status_code)
print("x.ai body:", resp.text)

# 尽量从返回中取内容，失败则给出错误信息
data = {}
try:
    data = resp.json()
except Exception:
    pass

content = (
    data.get("choices", [{}])[0]
    .get("message", {})
    .get("content", f"情报生成失败：{resp.status_code} {resp.text}")
)
# 企业微信 markdown.content 最大 4096 字节，这里按字符粗略限制
MAX_LEN = 3800
if len(content) > MAX_LEN:
    content = content[:MAX_LEN] + "\n\n（内容过长，已截断显示）"
# 发送到企业微信群
wechat_data = {
    "msgtype": "markdown",
    "markdown": {
        "content": (
            f"<@all>\n"
            f"# 煤化工全行业情报（豪华版）\n"
            f"**{now_str}**\n\n"
            f"{content}\n\n"
            f"> 永久免费 | 每日8点"
        )
    },
}

resp2 = requests.post(WEBHOOK, json=wechat_data, timeout=10)
print("WeChat status:", resp2.status_code, "body:", resp2.text)
