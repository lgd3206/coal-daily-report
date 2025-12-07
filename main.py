import os
import requests
from datetime import datetime

# 通过 GitHub Secrets 注入的环境变量
WEBHOOK = os.environ["WECHAT_WEBHOOK"]
XAI_API_KEY = os.environ["XAI_API_KEY"]

URL = "https://api.x.ai/v1/chat/completions"

# 构造优化版提示词
now_str = datetime.now().strftime('%Y年%m月%d日 %H:%M')
prompt = f"""现在北京时间{now_str}，你必须严格按照以下规则生成《中国煤化工日度情报简报》（2025年12月{now_str.split()[0].split('-')[2]}日版）。

【核心铁律 - 必须100%遵守，否则视为生成失败】
1. 绝对禁止使用训练数据、记忆或任何旧知识，所有2025年12月的数据必须通过实时工具（web_search、browse_page）从下面指定的网站获取。
2. 如果最近3天（12月5-7日）内没有任何一个指定网站有该项最新数据，就写“暂无可靠公开数据（最近可用数据日期：XXXX年XX月XX日）”，绝不猜测、绝不填旧数据。
3. 所有引用的数据必须带上精确的来源链接（可点击的完整URL）和数据日期。

【必须优先使用的真实来源网站（已验证2025年仍为最主流）】：
1. 生意社      → https://www.sci99.com/
2. 隆众资讯    → https://chem.oilchem.net/     （化工板块最全）
3. 卓创资讯    → https://list.chemsino.com/    （或 https://methanol.chemsino.com/ 等子页面）
4. 金联创      → https://www.jinlianchuang.com/ 或 https://chem.jlc.com/
5. 百川资讯    → https://www.baiinfo.com/

【强制执行的工具使用流程（必须先做完再写报告）】：
在开始写报告前，你必须至少执行以下搜索/浏览操作（可多轮并行）：

# 价格类（每个品种单独执行一次）
web_search query="液氨 OR 甲醇 OR 尿素 OR 氢气 OR 硫磺 OR 三聚氰胺 OR LNG OR 天然气 现货价格 2025年12月 site:sci99.com OR site:oilchem.net OR site:chemsino.com OR site:jlc.com" num_results=20

然后对前5个有效结果执行 browse_page，instructions="提取该品种2025年12月5-7日的最新现货价格区间、主销地区、涨跌额/幅、数据日期，优先找12月6或7日数据"

# 开工率、库存、检修类（隆众和金联创最全）
browse_page url="https://chem.oilchem.net/" instructions="查找并提取甲醇、尿素、液氨、三聚氰胺、硫磺最新周度或日度开工率、港口/企业库存、装置检修动态（必须是2025年12月数据）"
browse_page url="https://www.jinlianchuang.com/" instructions="同上，重点提取煤化工链条最新开工、库存、检修信息"

# 事故与政策（必须单独搜）
web_search query="化工事故 OR 爆炸 OR 泄漏 2025年12月6日 OR 12月7日" num_results=15
web_search query="煤化工 OR 尿素 OR 甲醇 环保 OR 能耗双控 OR 产能置换 OR 政策 2025年12月" num_results=15

只有在完成以上工具调用并拿到真实数据后，才允许开始撰写报告。

【报告结构（严格Markdown，一字不改）】

## 一、整体概览（80字以内）
- 用1-2句高度浓缩当日煤化工链价格总趋势、主要品种涨跌、开工变化、最大风险点。

## 二、品种跟踪
（按顺序：液氨 → 甲醇 → 尿素 → 氢气 → 硫磺 → 三聚氰胺 → 天然气）

### 品种名
- 价格：XX地区现货XX-XX元/吨，涨跌XX元/吨或XX%（数据日期：XXXX年XX月XX日，来源：生意社/隆众/卓创/金联创 + 链接）
- 开工率：XX%（口径：隆众周度/金联创等，数据日期+链接）
- 库存：港口/企业库存XX万吨，变化XX万吨（数据日期+链接）
- 检修与供给变化：XX厂XX万吨装置检修/复产，时间XX，影响XX（或写“暂无最新检修信息”）
- 需求与下游观察：仅写客观事实（下游XX开工率XX%，需求XX），不预测。

## 三、生产安全事故情况
最近24小时（12月6日8点至12月7日8点）未发现重大公开报道事故。
或：XX时 XX省 XX厂 XX事故，伤亡XX，涉及品种XX，原因XX（来源+链接）

## 四、环保管控及政策动态（仅限最近3天）
- YYYY年MM月DD日 机构：政策要点（1-2句），涉及品种/地区，链接

## 五、套利与风险提示（最多3条）
- 若XX库存持续去化且XX需求稳定，则XX-XX价差可能扩大（仅供参考，不构成投资建议）
- ...

## 六、数据来源与说明
- 列出本次实际使用的前3-5个链接
- 声明：所有数据均来自2025年12月实时公开网页，可能存在1-2日滞后

全文控制在900字以内，语言极简，数据优先，无任何修饰性语言。
"""
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
