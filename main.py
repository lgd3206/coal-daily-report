import os
import requests
from datetime import datetime

# 通过 GitHub Secrets 注入的环境变量
WEBHOOK = os.environ["WECHAT_WEBHOOK"]
XAI_API_KEY = os.environ["XAI_API_KEY"]

URL = "https://api.x.ai/v1/chat/completions"

# 构造优化版提示词
now_str = datetime.now().strftime('%Y年%m月%d日 %H:%M')
day_str = datetime.now().strftime('%d')
prompt = f"""现在北京时间{now_str}，请根据今天的最新市场数据生成《中国煤化工日度情报简报》。

【信息获取要求】
请使用你的实时搜索能力，从以下来源获取2025年12月6-7日的最新数据：

重点数据源（按优先级）：
1. 生意社 https://www.sci99.com/ - 商品价格行情
2. 隆众资讯 https://chem.oilchem.net/ - 开工率、库存、价格
3. 卓创资讯 https://list.chemsino.com/ 或 https://methanol.chemsino.com/ - 甲醇等细分
4. 金联创 https://www.jinlianchuang.com/ 或 https://chem.jlc.com/ - 煤化工综合数据
5. 百川资讯 https://www.baiinfo.com/ - 补充数据

【必须搜索的内容】
A) 商品价格（搜索：液氨、甲醇、尿素、氢气、硫磺、三聚氰胺、LNG/天然气 2025年12月最新现货价格）
B) 开工率库存（搜索：甲醇开工率、尿素库存、液氨装置、硫磺、三聚氰胺 2025年12月）
C) 检修信息（搜索：化工装置检修、煤化工停产、装置开车 2025年12月）
D) 事故信息（搜索：化工事故、安全 2025年12月6-7日）
E) 政策动态（搜索：化工政策、环保管控、能耗双控 2025年12月）

【报告生成要求】

## 一、整体概览（80字以内）
用1-2句高度浓缩当日煤化工链价格总趋势、主要品种涨跌、开工变化、最大风险点。

## 二、品种跟踪（按顺序：液氨 → 甲醇 → 尿素 → 氢气 → 硫磺 → 三聚氰胺 → 天然气）

对于每个品种，请提供：
- 价格：最新现货价格（元/吨）、涨跌幅、数据日期、来源网站
- 开工率：最新开工率%、数据来源
- 库存：最新库存数据、变化情况、数据来源
- 检修与供给：最新检修/停产/开车信息
- 需求观察：客观下游需求变化

如果找不到某项数据，直接注明"暂无最新公开数据"，不要填充假数据。

## 三、生产安全事故情况
列出最近24小时内的重大安全事故（若有），包括：时间、地点、企业、事故类型、涉及品种、来源

如无事故，写"最近24小时未发现重大公开报道事故"

## 四、环保管控及政策动态
最近3天内的重要政策、管控措施、环保动向

## 五、套利与风险提示
基于当前市场数据提出的主要风险和套利机会（最多3条）

## 六、数据来源与说明
列出实际使用的数据来源网站和获取时间

【格式约束】
- 全文900-1200字
- 数据优先，语言简洁
- 所有价格数据必须注明：金额+单位+数据日期+来源网站
- 禁止猜测和填充：无数据则明确说"暂无公开数据"
- 日期统一格式：YYYY年MM月DD日 HH:00
"""

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
