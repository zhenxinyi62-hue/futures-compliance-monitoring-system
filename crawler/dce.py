import requests
from bs4 import BeautifulSoup
import json


def crawl_dce():

    url = "http://www.dce.com.cn/dce/xxfw/ggtz/index.html"


    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }


    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )


    response.encoding = "utf-8"


    print("DCE状态码:", response.status_code)

    print("DCE网页长度:", len(response.text))


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    announcements = []


    for a in soup.find_all("a"):

        title = a.get_text(
            strip=True
        )

        link = a.get(
            "href"
        )


        if not title:
            continue


        if (
            "公告" in title
            or "通知" in title
            or "提示" in title
        ):


            if link:

                if link.startswith("/"):

                    link = (
                        "http://www.dce.com.cn"
                        + link
                    )


                announcements.append(
                    {
                        "exchange": "DCE",
                        "title": title,
                        "type": "交易所公告",
                        "url": link
                    }
                )


    print(
        "DCE公告数量:",
        len(announcements)
    )


    return announcements



if __name__ == "__main__":


    data = crawl_dce()


    with open(
        "data/dce_announcements.json",
        "w",
        encoding="utf-8"
    ) as f:


        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


    print("DCE更新完成")
