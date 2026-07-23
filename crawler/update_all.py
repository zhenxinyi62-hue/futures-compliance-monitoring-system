import json
from datetime import datetime

data = [
    {
        "exchange": "SHFE",
        "title": "GitHub 自动更新测试",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "测试公告",
        "url": "https://example.com"
    }
]

with open("data/announcements.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("数据更新成功！")
