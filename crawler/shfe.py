import requests
from bs4 import BeautifulSoup
import json


def crawl_shfe():

    url = "https://www.shfe.cn/publicnotice/notice/"

    headers = {
        "User-Agent": 
        "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers
    )

    response.encoding = "utf-8"
    print("SHFE更新完成")
    
    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )
    print(response.text[:500])

    announcements = []


  # 查找公告列表

for item in soup.find_all("a"):

    title = item.get_text(strip=True)

    link = item.get("href")


    if (
        title
        and len(title) > 5
        and ("公告" in title or "通知" in title)
    ):

        if link and link.startswith("/"):
            link = "https://www.shfe.com.cn" + link


        announcements.append(
            {
                "exchange": "SHFE",
                "title": title,
                "type": "交易所公告",
                "url": link
            }
        )


    return announcements



if __name__ == "__main__":

    data = crawl_shfe()


    with open(
        "data/announcements.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


    print("SHFE更新完成")
