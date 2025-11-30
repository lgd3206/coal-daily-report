import os
import requests
from datetime import datetime

  # 从 GitHub Secrets 传进来的环境变量里取
WEBHOOK = os.environ["WECHAT_WEBHOOK"]
XAI_API_KEY = os.environ["XAI_API_KEY"]

url = "https://api.x.ai/v1/chat/completions"

payload = {
      "model": "grok-3",
      "temperature": 0.2,
      "messages": [{
          "role": "user",
          "content": (
              f"现在北京时间{datetime.now().strftime('%Y年%m月%d日 %H:%M')}，"
              "给我煤化工全行业（甲醇、尿素、液氨、电石、PVC、BDO、乙二醇、烯烃）"
              "最新价格、开工率、库存、检修、事故、政策、套利机会，只给事实和数字，"
              "控制1000字以内，用中文"
          )
      }],
}

headers = {
      "Authorization": f"Bearer {XAI_API_KEY}",
      "Content-Type": "application/json",
}

try:
      r = requests.post(url, json=payload, headers=headers, timeout=40)
      print("x.ai status:", r.status_code)
      print("x.ai body:", r.text)  # 调试时看具体返回
      r.raise_for_status()
      content = r.json()["choices"][0]["message"]["content"]
except Exception as e:
      content = f"情报生成失败：{e}\n请稍后重试或联系管理员"

data = {
      "msgtype": "markdown",
      "markdown": {
          "content": (
              f"<@all>\n# 煤化工全行业情报（豪华版）\n"
              f"**{datetime.now().strftime('%Y年%m月%d日 %H:%M')}**\n\n"
              f"{content}\n\n> 永久免费 | 每日8点"
          )
      },
}

requests.post(WEBHOOK, json=data)
print("豪华版日报已发送")
