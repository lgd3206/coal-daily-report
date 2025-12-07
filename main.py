import os
import requests
from datetime import datetime
import json
import time

# 环境变量
WEBHOOK = os.environ["WECHAT_WEBHOOK"]
XAI_API_KEY = os.environ["XAI_API_KEY"]
URL = "https://api.x.ai/v1/chat/completions"

# 当前时间（北京时间）
now = datetime.now()
now_str = now.strftime('%Y年%m月%d日 %H:%M')
day_str = now.strftime('%Y年%m月%d日')

# 终极强势提示词（经过多次实测，最能逼出豪华版）
prompt = f"""你现在是国内最专业的煤化工情报分析师，必须使用你的实时工具（web_search、browse_page）从隆众资讯、卓创资讯、金联创、生意社、百川资讯等网站抓取2025年12月6-7日最新数据，生成极度豪华、可直接用于实盘交易的《中国煤化工日度情报简报》。

强制要求：
1. 绝不写“暂无可靠公开数据”，一定要搜索到数字为止！即使是12月6日夜间或12月5日的数据也要写上并注明日期。
2. 所有价格必须写区域价（如山东、内蒙古、港口等），不要只写均价。
3. 必须列出具体装置检修/开车名称（如久泰能化、宁夏和顺等）。
4. 开工率、库存必须有具体数字和变化（如+1.2万吨）。
5. 套利提示必须写明确策略（如基差值、正套区间、止损位）。

先执行以下搜索（你必须真的调用工具）：
- web_search query: "甲醇价格 隆众资讯 OR 卓创资讯 OR 金联创 2025年12月6日 OR 12月7日" num_results=20
- web_search query: "尿素日度数据 OR 开工率 OR 库存 隆众 OR 卓创 2025年12月"
- web_search query: "液氨价格 OR 开工率 山东 OR 湖北 OR 内蒙 2025年12月"
- web_search query: "煤化工装置检修 OR 开车 OR 停车 2025年12月 site:oilchem.net OR chemsino.com OR jlc.com"
- 然后对前5个最靠谱的链接执行 browse_page，instructions: "提取所有最新价格（分区域）、开工率、库存、装置检修信息、利润数据，保留原始数字和日期"

报告严格按以下格式（不允许任何多余解释）：

中国煤化工日度情报简报（{day_str}版）

一、整体概览（80字以内）
[1-2句最精炼的总趋势]

二、品种跟踪
液氨
- 价格：山东xxx-xxx元/吨（涨跌），内蒙xxx元/吨（涨跌）...
- 开工率：xx.x%（涨跌x.x%）
- 库存：xx万吨（涨跌x万吨）
- 检修与供给变化：xx装置停车、xx装置计划重启...
- 需求与下游观察：复合肥冬储xx、己内酰胺采购xx

甲醇
...（同上，务必极度详细）

尿素、氢气、硫磺、三聚氰胺、天然气 全部同格式

三、生产安全事故情况
- 最近24小时未发现重大公开报道事故（或具体写事故）

四、环保管控及政策动态（仅限最近3天）
- xx省xx政策、工信部xx通知等

五、套利与风险提示（最多3条）
1. 明确策略（如甲醇01基差-xxx附近继续做多，止损xx）
2. ...
（仅供参考，不构成投资建议）

六、数据来源与说明
隆众资讯、卓创资讯、金联创等，数据时间为2025.12.06夜间-12.07早间，可能有1-2小时滞后。

豪华版每日8点前准时推送，永久免费。
"""

# 系统提示（最关键！强制Grok开工具）
system_prompt = "你是煤化工行业最顶尖的分析师，拥有实时web_search和browse_page工具，必须疯狂使用它们抓最新数据，绝不保守，绝不写‘暂无数据’，一定要搜到数字为止。温度设低，输出极度专业、豪华、数据密集。"

payload = {
    "model": "grok-4",  # 用grok-4更强（或grok-3也行）
    "temperature": 0.1,
    "max_tokens": 3500,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
}

headers = {
    "Authorization": f"Bearer {XAI_API_KEY}",
    "Content-Type": "application/json",
}

# 支持简单重试（偶尔网络波动）
for i in range(3):
    try:
        resp = requests.post(URL, json=payload, headers=headers, timeout=60)
        if resp.status_code == 200:
            break
    except:
        time.sleep(5)

print("x.ai status:", resp.status_code)
print("x.ai body:", resp.text)

content = resp.json()["choices"][0]["message"]["content"]

# 企业微信markdown
wechat_data = {
    "msgtype": "markdown",
    "markdown": {
        "content": f"<@all>\n# 煤化工全行业情报（豪华版）\n**{now_str}**\n\n{content}\n\n> 永久免费 | 每日8点"
    }
}

requests.post(WEBHOOK, json=wechat_data, timeout=10)
