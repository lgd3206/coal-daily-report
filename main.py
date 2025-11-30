import os
from datetime import datetime
import requests

WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ebd19a11-21db-43eb-b53d-61d3d010da8f"

def get_report():
    # 模拟Grok调用（生产中替换为API）
    return "液氨价格: 2400-2600元/吨；开工率: 85%；库存: 150万吨。详情见附件。"

content = get_report()
data = {
    "msgtype": "markdown",
    "markdown": {"content": f"# 每日情报\n{datetime.now().strftime('%Y-%m-%d')}\n\n{content}"}
}
requests.post(WEBHOOK, json=data)
