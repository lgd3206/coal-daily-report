import requests
from datetime import datetime

WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ebd19a11-21db-43eb-b53d-61d3d010da8f"

def get_report():
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": "Bearer sk-beta-XXXXXXXXXXXXXXXXXXXXXXXX"}
    payload = {
        "messages": [{"role": "user", "content": f"现在北京时间{datetime.now().strftime('%Y年%m月%d日 %H:%M')}，给我煤化工全行业（甲醇、尿素、液氨、电石、PVC、BDO、乙二醇、烯烃）最新价格、开工率、库存、检修、事故、政策、套利机会，只给事实和数字，控制1000字以内，用中文"}],
        "model": "grok-beta",
        "temperature": 0.2
    }
    r = requests.post(url, json=payload, headers=headers, timeout=35)
    return r.json()['choices'][0]['message']['content']

content = get_report()

# 豪华版标题 + 自动@全体成员（可删）
data = {
    "msgtype": "markdown",
    "markdown": {
        "content": f"<@all>\n# 煤化工全行业情报（豪华版）\n**{datetime.now().strftime('%Y年%m月%d日 %H:%M')}**\n\n{content}\n\n> 由Grok实时生成 | 永久免费 | 每日8点准时推送"
    }
}

requests.post(WEBHOOK, json=data)
print("豪华版日报已发送")
